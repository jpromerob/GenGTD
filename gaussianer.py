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

from scipy import stats



""" This class defines a C-like struct """
class mu_ss_payload(Structure):
    _fields_ = [("mu_x_k", c_float),
                ("mu_y_k", c_float),
                ("mu_z_k", c_float),
                ("ss_x_k", c_float),
                ("ss_y_k", c_float),
                ("ss_z_k", c_float),
                ("mu_x_1", c_float),
                ("mu_y_1", c_float),
                ("mu_z_1", c_float),
                ("ss_x_1", c_float),
                ("ss_y_1", c_float),
                ("ss_z_1", c_float),
                ("mu_x_2", c_float),
                ("mu_y_2", c_float),
                ("mu_z_2", c_float),
                ("ss_x_2", c_float),
                ("ss_y_2", c_float),
                ("ss_z_2", c_float),
                ("mu_x_3", c_float),
                ("mu_y_3", c_float),
                ("mu_z_3", c_float),
                ("ss_x_3", c_float),
                ("ss_y_3", c_float),
                ("ss_z_3", c_float)]

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True

'''
For each axis, this function produces 3 'basic' PDFs (one per camera) plus 1 'special' PDF (from their product)
The function plots the 4 PDFs (in 3 subplots, one per axis) and returns 'xyz' and 'pdf'
'xyz' is the array of coordinates; 'pdf' is a matrix with the generated PDFs
'''
def generate_pdfs(nb_pts, pdf_center, mu, sigma):
    
    base_xyz = np.linspace(stats.norm.ppf(0.05), stats.norm.ppf(0.95), nb_pts)
    xyz = np.zeros((3,nb_pts))
    pdf = np.zeros((5,3,nb_pts))   
    
    
    # Generating PDFs (+ prodcuts and mixtures)
    for j in range(3): # x, y, z

        
        # This is done to re-center xyz array (for visual purposes)
        xyz[j,:] = base_xyz  + pdf_center[j] 

        # Checking output of each camera
        for i in range(3+1): # Cam 1, 2, 3, prod
      
            # PDF is calculated, using stats, with the purpose of visualization (not needed for pose merging)
            pdf[i,j,:] = stats.norm.pdf(xyz[j,:], mu[j,i], sigma[j,i]) 
    
    return xyz, pdf

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

        buff = csock.recv(1024)
        counter = 0
        while buff:
            counter += 1
            payload_in = mu_ss_payload.from_buffer_copy(buff) 

            if counter == 20:
                counter = 0
                # print("mu_3: ({:.3f}, {:.3f}, {:.3f}) | ss_3: ({:.3f}, {:.3f}, {:.3f})".format(payload_in.mu_x_k, payload_in.mu_y_k, payload_in.mu_z_k, payload_in.ss_x_k, payload_in.ss_y_k, payload_in.ss_z_k))

            data_queue.put([payload_in.mu_x_1,
                            payload_in.mu_x_2,
                            payload_in.mu_x_3,
                            payload_in.mu_x_k,
                            payload_in.mu_y_1,
                            payload_in.mu_y_2,
                            payload_in.mu_y_3,
                            payload_in.mu_y_k,
                            payload_in.mu_z_1,
                            payload_in.mu_z_2,
                            payload_in.mu_z_3,
                            payload_in.mu_z_k,
                            payload_in.ss_x_1,
                            payload_in.ss_x_2,
                            payload_in.ss_x_3,
                            payload_in.ss_x_k,
                            payload_in.ss_y_1,
                            payload_in.ss_y_2,
                            payload_in.ss_y_3,
                            payload_in.ss_y_k,
                            payload_in.ss_z_1,
                            payload_in.ss_z_2,
                            payload_in.ss_z_3,
                            payload_in.ss_z_k])


            

            buff = csock.recv(1024)

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
def animate(i, data_queue, axs, mu_ss):

    global killer

    
    while not data_queue.empty():
        mu_ss = data_queue.get(False)

    mu = np.zeros((3,4))
    sigma = np.zeros((3,4))



    # mu(x) for cams #1|#2|#3 and consolidated
    mu[0,0] = mu_ss[0]
    mu[0,1] = mu_ss[1]
    mu[0,2] = mu_ss[2]
    mu[0,3] = mu_ss[3]

    # mu(y) for cams #1|#2|#3 and consolidated
    mu[1,0] = mu_ss[4]
    mu[1,1] = mu_ss[5]
    mu[1,2] = mu_ss[6]
    mu[1,3] = mu_ss[7]

    # mu(z) for cams #1|#2|#3 and consolidated
    mu[2,0] = mu_ss[8]
    mu[2,1] = mu_ss[9]
    mu[2,2] = mu_ss[10]
    mu[2,3] = mu_ss[11]


    # ss(x) for cams #1|#2|#3 and consolidated
    sigma[0,0] = mu_ss[12]
    sigma[0,1] = mu_ss[13]
    sigma[0,2] = mu_ss[14]
    sigma[0,3] = mu_ss[15]

    # ss(y) for cams #1|#2|#3 and consolidated
    sigma[1,0] = mu_ss[16]
    sigma[1,1] = mu_ss[17]
    sigma[1,2] = mu_ss[18]
    sigma[1,3] = mu_ss[19]

    # ss(z) for cams #1|#2|#3 and consolidated
    sigma[2,0] = mu_ss[20]
    sigma[2,1] = mu_ss[21]
    sigma[2,2] = mu_ss[22]
    sigma[2,3] = mu_ss[23]

    print("mu_3: ({:.3f}, {:.3f}, {:.3f}))".format(mu[0,3], mu[1,3], mu[2,3]))

    nb_pts = 1000


    pdf_center = [-0.3, 0.5, 1.0, 1.0]
    height = 5

    ####################################################################################
    # Visualize Gaussians
    ####################################################################################
    xyz, pdf = generate_pdfs(nb_pts, pdf_center, mu, sigma) 

    labels = ['Cam 1', 'Cam 2', 'Cam3', 'Prod']
    colors = ['#5b9ad5', '#6fad47', '#febf00', '#000000']
    styles = ['--', '-.', ':' , '-']

    axs[0].clear()
    axs[1].clear()
    axs[2].clear()
    for k in range(3+1): # 1,2,3, product

        axs[0].plot(xyz[0,:], pdf[k,0,:], color=colors[k], label=labels[k], linestyle = styles[k])
        # axs[0].xaxis.set_visible(False)
        axs[0].set_ylim([0,height])
        axs[0].set_ylabel('x')

        axs[1].plot(xyz[1,:], pdf[k,1,:], color=colors[k], label=labels[k], linestyle = styles[k])
        # axs[1].xaxis.set_visible(False)
        axs[1].set_ylim([0,height])
        axs[1].set_ylabel('y')

        axs[2].plot(xyz[2,:], pdf[k,2,:], color=colors[k], label=labels[k], linestyle = styles[k])
        # axs[2].xaxis.set_visible(False)
        axs[2].set_ylim([0, height])
        axs[2].set_ylabel('z')


    max_pdf = pdf.max()

    axs[0].legend()   
    axs[1].legend()   
    axs[2].legend()   
    
    x_center = xyz[0,np.argmax(pdf[3,0,:])]
    y_center = xyz[1,np.argmax(pdf[3,1,:])]
    z_center = xyz[2,np.argmax(pdf[3,2,:])]
    
    delta = 2
    
    min_x = 0.1*int(10*(x_center-delta))
    max_x = 0.1*int(10*(x_center+delta))
    min_y = 0.1*int(10*(y_center-delta))
    max_y = 0.1*int(10*(y_center+delta))
    min_z = 0.1*int(10*(z_center-delta))
    max_z = 0.1*int(10*(z_center+delta))
    
    axs[0].set_xlim([x_center - delta, x_center + delta])
    axs[1].set_xlim([y_center - delta, y_center + delta])
    axs[2].set_xlim([z_center - delta, z_center + delta])
    axs[0].set_ylim([0, max_pdf])
    axs[1].set_ylim([0, max_pdf])
    axs[2].set_ylim([0, max_pdf])

    axs[0].set_xlabel('$x_w$')
    axs[1].set_xlabel('$y_w$')
    axs[2].set_xlabel('$z_w$')

    axs[0].set_xticks(np.arange(min_x, max_x, 0.1))
    axs[1].set_xticks(np.arange(min_y, max_y, 0.1))
    axs[2].set_xticks(np.arange(min_z, max_z, 0.1))

    if killer.kill_now:
        quit()


def anima_main(data_queue):

    # Create figure for plotting
    fig, axs = plt.subplots(3)
    
    pdfs = []

    i = 0
    mu_ss = 50*np.ones(24)

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(data_queue, axs, mu_ss), interval=1)
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
