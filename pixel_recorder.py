
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
    _fields_ = [("id", c_float),
                ("x", c_float),
                ("y", c_float)]



class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


def pixel_main(pixel_queue, nb_port):


    server_addr = ("172.16.222.46", nb_port)
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    try:
        # bind the server socket and listen
        ssock.bind(server_addr)
        print("Bind done")
        ssock.listen(3)
        print("Server listening on port {:d}".format(nb_port))

        # while True:
        csock, client_address = ssock.accept()
        print("Accepted connection from {:s}".format(client_address[0]))

        buff = csock.recv(512)
        while buff:
            payload_in = Payload.from_buffer_copy(buff) 
            pixel_queue.put([payload_in.id, payload_in.x, payload_in.y])
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
        
    print("c'est fini pixel_main")

def file_main(pixel_queue, d_source):

    global killer

    import time
    filename = "rec_px_" + d_source + "_" + time.strftime("%Y%m%d_%H%M") + ".csv"
    print(filename)

    f = open(filename,'w')

    pixel = [0.0,0.0,0.0]

    start_time = time.time()
    while not killer.kill_now:

        
        if not pixel_queue.empty():
            pixel = pixel_queue.get(False)

        end_time = time.time()

        time_elapsed = (end_time - start_time)
        if time_elapsed >= 1/100:
            start_time = time.time()
            line_pixel = '{: 3.3f},{: 3.3f},{: 3.3f}\n'.format(pixel[0], pixel[1], pixel[2]) # id, x, y
            f.write(line_pixel)
            # print("OPT: (" + line_opt + ") vs SNN(" + line_pixel + ")\n\n\n")
        # print("OPT: (" + line_opt + ") vs SNN(" + line_pixel + ")\n\n\n")
    f.close()


if __name__ == '__main__':


    try:
        d_source = sys.argv[1]
        if d_source != "snn" and d_source != "opt":
            quit()
        else:
            print("Valid data source!")
            if d_source == "snn" : 
                nb_port = 2500
            if d_source == "opt" : 
                nb_port = 2700

    except:
        quit()

    global killer



    pixel_queue = multiprocessing.Queue()


    killer = GracefulKiller()



    p_pixel = Process(target=pixel_main, args=(pixel_queue,nb_port,))
    p_file = Process(target=file_main, args=(pixel_queue, d_source))
    
    p_pixel.start()
    p_file.start()


    p_file.join()
    p_pixel.join()


