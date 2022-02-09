
# coding: utf-8

'''

This script is meant to check that poses in world and camera space make sense

'''

import argparse
import attr
import signal
import natnet
import sys, getopt
import pdb
import time
import cv2 as cv
import matplotlib.pyplot as plt
import multiprocessing 
from dv import AedatFile
import numpy as np
import h5py
import math
from numpy import genfromtxt
import socket
import random
from ctypes import *
from multiprocessing import Process



""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float)]



global snn_xyz
global opt_xyz

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True

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

        global asset_id
        for b in rigid_bodies:
            if b.id_ == asset_id:
                ground_truth = [b.position[0], b.position[1], b.position[2], 1]
                opt_queue.put([b.position[0], b.position[1], b.position[2]])



def opt_main(opt_queue):    

    global asset_id

    try:
        asset_id = int(sys.argv[1])

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
        print("Usage: python3 live_pose <asset_id>")
        quit()


    try:
        app = ClientApp.connect()
        app.run()
    except natnet.DiscoveryError as e:
        print('Error:', e)

    print("c'est fini opt_main")

def snn_main(snn_queue):

    global snn_xyz

    PORT = 2600
    server_addr = ("172.16.222.46", PORT)
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    try:
        # bind the server socket and listen
        ssock.bind(server_addr)
        print("Bind done")
        ssock.listen(3)
        print("Server listening on port {:d}".format(PORT))

        # while True:
        csock, client_address = ssock.accept()
        print("Accepted connection from {:s}".format(client_address[0]))

        buff = csock.recv(512)
        while buff:
            payload_in = Payload.from_buffer_copy(buff) 
            snn_xyz = [payload_in.x, payload_in.y, payload_in.z]
            snn_queue.put([payload_in.x, payload_in.y, payload_in.z])
            buff = csock.recv(512)

            if killer.kill_now:
                break
        print("Closing connection to client")
        print("----------------------------")
        csock.close()

    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    except KeyboardInterrupt:
        ssock.close()
    finally:
        print("Closing socket")
        
    print("c'est fini snn_main")

def all_main(opt_queue, snn_queue):

    global killer

    f = open('opt_vs_snn.csv','w')

    opt_xyz = [0.0,0.0,0.0]
    snn_xyz = [0.0,0.0,0.0]

    start_time = time.time()
    while not killer.kill_now:

        
        if not opt_queue.empty():
            opt_xyz = opt_queue.get(False)
        if not snn_queue.empty():
            snn_xyz = snn_queue.get(False)

        end_time = time.time()

        time_elapsed = (end_time - start_time)
        if time_elapsed >= 1/100:
            start_time = time.time()
            line_snn = '{: 3.3f},{: 3.3f},{: 3.3f}'.format(snn_xyz[0], snn_xyz[1], snn_xyz[2])
            line_opt = '{: 3.3f},{: 3.3f},{: 3.3f}'.format(opt_xyz[0], opt_xyz[1], opt_xyz[2])
            line_all = line_opt + "," + line_snn + "\n"
            f.write(line_all)
            # print("OPT: (" + line_opt + ") vs SNN(" + line_snn + ")\n\n\n")
        # print("OPT: (" + line_opt + ") vs SNN(" + line_snn + ")\n\n\n")
    f.close()


if __name__ == '__main__':


    global killer
    global snn_xyz
    global opt_xyz


    opt_queue = multiprocessing.Queue()
    snn_queue = multiprocessing.Queue()


    killer = GracefulKiller()



    snn_xyz = [0.0, 0.0, 0.0]
    opt_xyz = [0.0, 0.0, 0.0]

    global f


    p_opt = Process(target=opt_main, args=(opt_queue,))
    p_snn = Process(target=snn_main, args=(snn_queue,))
    p_all = Process(target=all_main, args=(opt_queue, snn_queue,))
    
    p_opt.start()
    p_snn.start()
    p_all.start()


    p_all.join()
    p_snn.join()
    p_opt.join()


