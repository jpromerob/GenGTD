import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import math


# import argparse
# import attr
import signal
# import natnet
import sys
# import pdb
# import cv2 as cv
import multiprocessing 
# from dv import AedatFile
import numpy as np
# import h5py
# from numpy import genfromtxt
import socket
# import random
from ctypes import *
from multiprocessing import Process

""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float)]

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


def data_main(data_queue, nb_port):

    global killer

    i = 0
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

        buff = csock.recv(sizeof(Payload))
        counter = 0
        while buff:
            counter += 1
            payload_in = Payload.from_buffer_copy(buff) 
            if counter == 1:
                data_queue.put([payload_in.x, payload_in.y, payload_in.z])
                counter = 0
            # print([payload_in.x, payload_in.y, payload_in.z])

            # i += 1
            # x = math.sin((0+i*5)*math.pi/180)+0.5
            # y = math.sin((90+i*5)*math.pi/180)+0.5
            # z = math.sin((45+i*5)*math.pi/180)+0.5
            # data_queue.put([x, y, z])

            buff = csock.recv(sizeof(Payload))

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
        
    print("c'est fini data_main")


# This function is called periodically from FuncAnimation
def animate(i, data_queue, axs, t, x, y, z, xyz):

    global killer

    while not data_queue.empty():
        xyz = data_queue.get(False)

    # Add x and y to lists
    t.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    x.append(xyz[0])
    y.append(xyz[1])
    z.append(xyz[2])

    # Limit x and y lists to 100 items
    t = t[-100:]
    x = x[-100:]
    y = y[-100:]
    z = z[-100:]

    txt_x = txt_y = txt_z = "No signal"
    if x[-1] != -100:
        txt_x = "x = {:.3f} [m] ".format(x[-1]) 
    if y[-1] != -100:
        txt_y = "y = {:.3f} [m] ".format(y[-1]) 
    if z[-1] != -100:
        txt_z = "z = {:.3f} [m] ".format(z[-1]) 

    # Draw x and y lists
    axs[0].clear()
    axs[0].plot(t, x, color='r')
    axs[0].text(t[0], 0.1, txt_x, fontsize='xx-large')
    axs[0].xaxis.set_visible(False)
    axs[0].set_ylim([-0.7,0.3])
    axs[0].set_ylabel('x')

    axs[1].clear()
    axs[1].plot(t, y, color='g')
    axs[1].text(t[0], 0.8, txt_y, fontsize='xx-large')
    axs[1].xaxis.set_visible(False)
    axs[1].set_ylim([0,1])
    axs[1].set_ylabel('y')

    axs[2].clear()
    axs[2].plot(t, z, color='b')
    axs[2].text(t[0], 1.3, txt_z, fontsize='xx-large')
    axs[2].xaxis.set_visible(False)
    axs[2].set_ylim([0.5,1.5])
    axs[2].set_ylabel('z')

    axs[0].set_title("Object Position in Workspace")

    if killer.kill_now:
        quit()


def anima_main(data_queue):

    # Create figure for plotting
    fig, axs = plt.subplots(3, figsize=(8, 12))

    t = []
    x = []
    y = []
    z = []

    i = 0
    xyz = [-100,-100,-100]

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(data_queue, axs, t, x, y, z, xyz), interval=1)
    plt.show()


if __name__ == '__main__':
    
    global killer

    killer = GracefulKiller()
    
    try:
        d_source = sys.argv[1]
        if d_source != "snn" and d_source != "opt" and d_source != "all":
            quit()
        else:
            print("Valid data source!")
            if d_source == "snn" : 
                nb_port = 2500
            if d_source == "opt" : 
                nb_port = 2700
            if d_source == "all" : 
                nb_port = 2600

    except:
        quit()

    data_queue = multiprocessing.Queue()

    p_data = Process(target=data_main, args=(data_queue,nb_port,))
    p_anima = Process(target=anima_main, args=(data_queue,))
    
    p_data.start()
    p_anima.start()


    p_data.join()
    p_anima.join()
