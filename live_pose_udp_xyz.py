
# coding: utf-8

'''

This script is meant to check that poses in world and camera space make sense

'''

import argparse
import attr
import natnet
import sys, getopt
import pdb
import time
import cv2 as cv
import matplotlib.pyplot as plt
from dv import AedatFile
import numpy as np
import h5py
import math
from numpy import genfromtxt
import socket
import random
from ctypes import *


""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float),
                ("p", c_float)]

'''
This function sets the camera poses based on manual readings from optitrack (usin camera marker 'hat')
'''
def set_cam_poses():
    cam_poses = np.zeros((3,6))

    # Cam 1
    cam_poses[0,0] = -0.099 # cam1:cx
    cam_poses[0,1] = 0.968 # cam1:cy
    cam_poses[0,2] = 1.363 # cam1:cz
    cam_poses[0,3] = (math.pi/180)*(-71.499) # cam1:alpha
    cam_poses[0,4] = (math.pi/180)*(16.753) # cam1:beta
    cam_poses[0,5] = (math.pi/180)*(-20.992) # cam1:gamma

    # Cam 2
    cam_poses[1,0] = -0.570 # cam2:cx
    cam_poses[1,1] = 0.970 # cam2:cy
    cam_poses[1,2] = 1.395 # cam2:cz
    cam_poses[1,3] = (math.pi/180)*(-62.113) # cam2:alpha
    cam_poses[1,4] = (math.pi/180)*(-42.374) # cam2:beta
    cam_poses[1,5] = (math.pi/180)*(-6.134) # cam2:gamma

    # Cam 3
    cam_poses[2,0] = -0.664 # cam3:cx
    cam_poses[2,1] =  0.979 # cam3:cy
    cam_poses[2,2] =  0.538 # cam3:cz
    cam_poses[2,3] = (math.pi/180)*(148.698)# cam3:alpha
    cam_poses[2,4] = (math.pi/180)*(-46.056)# cam3:beta
    cam_poses[2,5] = (math.pi/180)*(148.752)# cam3:gamma

    return cam_poses


'''
This function returns the matrix 'c2w' that converts coordinates in camera space to coordinates in world space.
'''
def get_transmats(cam_poses):
    
    c2w = np.zeros((4,4,3))
    for i in range(3): # Cam 1, 2, 3
        
        cx = cam_poses[i,0]
        cy = cam_poses[i,1]
        cz = cam_poses[i,2]
        alpha = cam_poses[i,3]
        beta = cam_poses[i,4] 
        gamma = cam_poses[i,5]

        # Transformation matrices (translation + rotations around x, y, z)
        mat_tran = np.array([[1,0,0,cx],
                             [0,1,0,cy],
                             [0,0,1,cz],
                             [0,0,0,1]])

        mat_rotx = np.array([[1,0,0,0],
                             [0,math.cos(alpha), -math.sin(alpha),0],
                             [0, math.sin(alpha), math.cos(alpha),0],
                             [0,0,0,1]])

        mat_roty = np.array([[math.cos(beta), 0, math.sin(beta),0],
                             [0,1,0,0],
                             [-math.sin(beta), 0, math.cos(beta),0],
                             [0,0,0,1]])


        mat_rotz = np.array([[math.cos(gamma), -math.sin(gamma), 0, 0],
                             [math.sin(gamma), math.cos(gamma),0, 0],
                             [0,0,1,0],
                             [0,0,0,1]])

        # General transformation matrix 'camera to world' (c2w)
        c2w[:,:,i] = mat_tran.dot(mat_rotz).dot(mat_roty).dot(mat_rotx)
    
    
    return c2w

'''
This function defines object pose from camera perspective
'''
def define_object_pose(c2w, ground_truth):
    
    perspective = np.zeros((4,3)) # coordinates|cameras
    # Checking output of each camera
    for i in range(3): # Cam 1, 2, 3
        w2c = np.linalg.inv(c2w[:,:,i])
        perspective[:, i] = w2c.dot(ground_truth)

    return perspective[0:3,:]


'''
This functions determines the angular 'distance' between camera and object in planez XZ and YZ
'''
def get_angles(obj_pose, cam_pose):
    angles = np.zeros(2)
    angles[0] = (180/math.pi)*math.atan2((obj_pose[0] - 0),(obj_pose[2] - 0)) + 180 # delta_x/delta_z
    angles[1] = (180/math.pi)*math.atan2((obj_pose[1] - 0),(obj_pose[2] - 0)) + 180 # delta_y/delta_z

    if(angles[0]>180):
        angles[0] = 360-angles[0]
    if(angles[1]>180):
        angles[1] = 360-angles[1]
    if(angles[0]<-180):
        angles[0] = 360+angles[0]
    if(angles[1]<-180):
        angles[1] = 360+angles[1]

    if(obj_pose[0] < 0):
        angles[0] = -angles[0]
    if(obj_pose[1] < 0):
        angles[1] = -angles[1]

    return angles






@attr.s
class ClientApp(object):

    _client = attr.ib() 

    @classmethod
    def connect(cls):
        client = natnet.Client.connect()
        if client is None:
            return None
        return cls(client)

    def run(self):
        self._client.set_callback(self.callback)
        self._client.spin()

    def callback(self, rigid_bodies, markers, timing):

        global cam_poses, c2w, cam_id, asset_id
        
        for b in rigid_bodies:
            if b.id_ == asset_id:
                ground_truth = [b.position[0], b.position[1], b.position[2], 1]
                cp = define_object_pose(c2w, ground_truth)
                angles = get_angles(cp[:,cam_id-1], np.array([0,0,0]))
                gt = c2w[:,:,cam_id-1].dot(np.array([cp[0,cam_id-1], cp[1,cam_id-1], cp[2,cam_id-1], 1]))
                line = ' ({: 3.3f},{: 3.3f},{: 3.3f}) --> ({: 3.3f},{: 3.3f},{: 3.3f}) | ({: 3.3f},{: 3.3f}) \n ({: 3.3f},{: 3.3f},{: 3.3f}) <--\n'.format(b.position[0], b.position[1], b.position[2],cp[0,cam_id-1], cp[1,cam_id-1], cp[2,cam_id-1], angles[0], angles[1], gt[0], gt[1], gt[2])

                port_nb = 3000 + cam_id%3 # cam #1 --> 3001 | cam #2 --> 3002 | cam #3 --> 3000

                print(port_nb)

                server_addr = ('172.16.222.31', port_nb)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    s.connect(server_addr)
                    presence = 1
                    payload_out = Payload(cp[0,cam_id-1], cp[1,cam_id-1], cp[2,cam_id-1], presence)
                    nsent = s.send(payload_out)
                except AttributeError as ae:
                    print("Error creating the socket: {}".format(ae))
                except socket.error as se:
                    print("Exception on socket: {}".format(se))
                    print(port_nb)
                finally:
                    s.close()

                print(line)

def main():    

    global cam_poses, c2w, cam_id, asset_id

    try:
        cam_id = int(sys.argv[1])
        asset_id = int(sys.argv[2]) # The id of the asset (hammer, stimulus, camhat) in optitrack

        if asset_id == 1:
            print("Showing hammer poses")
        elif asset_id == 2:
            print("Showing camhat poses")
        elif asset_id == 3:
            print("Showing stimulus poses")
        elif asset_id == 4:
            print("Showing HBP LED poses")
        else:
            print("Wrong asset_id (Hammer: 1, Camhat: 2, Stimulus: 3)")
            quit()

        time.sleep(3)

    except:
        print("Usage: python3 live_pose <cam_id> <asset_id>")
        quit()

    cam_poses = set_cam_poses()
    c2w = get_transmats(cam_poses)

    try:
        app = ClientApp.connect()
        app.run()
    except natnet.DiscoveryError as e:
        print('Error:', e)


if __name__ == '__main__':

    global f
    main()


