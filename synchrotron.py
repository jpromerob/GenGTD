import sys, getopt
import pdb
import time
import cv2 as cv
import matplotlib.pyplot as plt
from dv import AedatFile
import numpy as np
import h5py
from numpy import genfromtxt


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
        c2w[:,:,i] = mat_tran.dot(mat_rotx).dot(mat_roty).dot(mat_rotz)
    
    
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


if __name__ == "__main__":


    if len(sys.argv) == 2:
        version = sys.argv[1]
    else:
        print("\nTry: python3 synchrotron.py <dataset version>\n")
        quit()

    
    path = '/home/juan/CameraSetup/Recordings_3cams'
    pose_file = path + "/poses_v" + str(version) + ".csv"


    poses = genfromtxt(pose_file, delimiter=',')
    poses[:,0] = poses[:,0]*1000000


    idx = 0
    cp = poses[idx,:]
    in_sync = False

    hf = h5py.File('all_data.h5', 'w')

    for i in range(3):
        cam_id = i+1
        
        inputfile = path + "/cam"+ str(cam_id)+"/cam"+ str(cam_id)+ "_v" + str(version) + ".aedat4"

        start = time.time()

        ev_count = 0 # to count events

        # Giving info to user (about processing)
        next_print = 0 # when to print log
        sec_count = 0 # seconds elapsed

        adat_file = "all_data_cam" + str(cam_id) + "_v" + str(version) + ".csv"
        f = open(adat_file, 'a')
        with AedatFile(inputfile) as ifile:
            # loop through the "events" stream
            for e in ifile["undistortedEvents"]:     

                ev_count+= 1

                # Synchronization loop (since pose recording starts before event recording)
                while e.timestamp >= cp[0]:
                    idx += 1
                    cp = poses[idx,:]    

                line = '{:.0f},{: 3.0f},{: 3.0f},{: 3.6f},{: 3.6f},{: 3.6f}\n'.format(e.timestamp, e.x, e.y, cp[1], cp[2], cp[3])
                f.write(line)
                

                if next_print < e.timestamp:
                    next_print = e.timestamp + 1000000
                    print("Done with %d seconds" %(sec_count))
                    sec_count +=1 

        f.close()
            

        stop = time.time() 

        elapsed = stop - start
        print("Parser took: " + str(elapsed-1) + " seconds.")
        
        all_data = genfromtxt(adat_file, delimiter=',')
        hf.create_dataset("cam" +str(cam_id), data=all_data)


    hf.close()