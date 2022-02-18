import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import math
import argparse
import attr
import natnet

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

        for b in rigid_bodies:
            if b.id_ == 4:
                line = 'OPT ({: 3.3f},{: 3.3f},{: 3.3f})'.format(b.position[0], b.position[1], b.position[2])
                rawpt_queue.put([b.position[0], b.position[1], b.position[2]])
                # print(line)



def data_main(merge_queue, nb_port):

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

        buff = csock.recv(8192)
        counter = 0
        while buff:
            counter += 1
            payload_in = Payload.from_buffer_copy(buff) 
            if counter == 1:
                merge_queue.put([payload_in.x, payload_in.y, payload_in.z])
                counter = 0
            # print([payload_in.x, payload_in.y, payload_in.z])

            # i += 1
            # x = math.sin((0+i*5)*math.pi/180)+0.5
            # y = math.sin((90+i*5)*math.pi/180)+0.5
            # z = math.sin((45+i*5)*math.pi/180)+0.5
            # merge_queue.put([x, y, z])

            buff = csock.recv(8192)

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
def animate(i, merge_queue, rawpt_queue, axs, t, mx, my, mz, rx, ry, rz, merge_xyz, rawpt_xyz):

    global killer


    while not rawpt_queue.empty():
        rawpt_xyz = rawpt_queue.get(False)

    while not merge_queue.empty():
        merge_xyz = merge_queue.get(False)

    # Add x and y to lists
    t.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    mx.append(merge_xyz[0])
    my.append(merge_xyz[1])
    mz.append(merge_xyz[2])
    rx.append(rawpt_xyz[0])
    ry.append(rawpt_xyz[1])
    rz.append(rawpt_xyz[2])

    # Limit x and y lists to 100 items
    t = t[-100:]
    mx = mx[-100:]
    my = my[-100:]
    mz = mz[-100:]
    rx = rx[-100:]
    ry = ry[-100:]
    rz = rz[-100:]

    error_x_txt = "e(x): " + str(int(1000*abs(mx[-1] - rx[-1]))) + "mm"
    error_y_txt = "e(y): " + str(int(1000*abs(my[-1] - ry[-1]))) + "mm"
    error_z_txt = "e(z): " + str(int(1000*abs(mz[-1] - rz[-1]))) + "mm"

    d_square = (mx[-1] - rx[-1])*(mx[-1] - rx[-1])+(my[-1] - ry[-1])*(my[-1] - ry[-1])+(mz[-1] - rz[-1])*(mz[-1] - rz[-1])
    # print(d_square)

    error_d_text = "e(d): " + str(int(1000*math.sqrt(d_square)))+ "mm"

    # Draw x and y lists
    axs[0].clear()
    axs[0].plot(t, mx, color='r')
    axs[0].plot(t, rx, color='k', linestyle='--')
    axs[0].text(t[0], 0.1, error_x_txt, fontsize='xx-large')
    axs[0].xaxis.set_visible(False)
    axs[0].set_ylim([-0.7,0.3])
    axs[0].set_ylabel('x')

    axs[1].clear()
    axs[1].plot(t, my, color='g')
    axs[1].plot(t, ry, color='k', linestyle='--')
    axs[1].text(t[0], 0.8, error_y_txt, fontsize='xx-large')
    axs[1].xaxis.set_visible(False)
    axs[1].set_ylim([0,1])
    axs[1].set_ylabel('y')

    axs[2].clear()
    axs[2].plot(t, mz, color='b')
    axs[2].plot(t, rz, color='k', linestyle='--')
    axs[2].text(t[0], 1.3, error_z_txt, fontsize='xx-large')
    axs[2].xaxis.set_visible(False)
    axs[2].set_ylim([0.5,1.5])
    axs[2].set_ylabel('z')

    axs[0].set_title(error_d_text)

    if killer.kill_now:
        quit()


def anima_main(merge_queue, rawpt_queue):

    # Create figure for plotting
    fig, axs = plt.subplots(3, figsize=(8, 12))
    t = []
    mx = []
    my = []
    mz = []
    rx = []
    ry = []
    rz = []

    i = 0
    merge_xyz = [0,0,0]
    rawpt_xyz = [0,0,0]

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(merge_queue, rawpt_queue, axs, t, mx, my, mz, rx, ry, rz, merge_xyz, rawpt_xyz), interval=1)
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

    merge_queue = multiprocessing.Queue()
    rawpt_queue = multiprocessing.Queue()

    p_data = Process(target=data_main, args=(merge_queue,nb_port,))
    p_anima = Process(target=anima_main, args=(merge_queue,rawpt_queue,))
    
    p_data.start()
    p_anima.start()


    try:
        app = ClientApp.connect()
        app.run()
    except natnet.DiscoveryError as e:
        print('Error:', e)


    p_data.join()
    p_anima.join()
