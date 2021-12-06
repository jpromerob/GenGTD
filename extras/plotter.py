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


optitrack_data = genfromtxt("p_w.csv", delimiter=',')
cam_1 = genfromtxt("p_c_1.csv", delimiter=',')
cam_2 = genfromtxt("p_c_2.csv", delimiter=',')
cam_3 = genfromtxt("p_c_3.csv", delimiter=',')

# Create four polar axes and access them through the returned array
fig, axs = plt.subplots(4,3,figsize=(15,10))

axs[0,0].plot(optitrack_data[:,0], label='x_w')
axs[0,0].set_ylim([-2,2])
axs[0,1].plot(optitrack_data[:,1], label='y_w')
axs[0,1].set_ylim([-2,2])
axs[0,2].plot(optitrack_data[:,2], label='z_w')
axs[0,2].set_ylim([-2,2])
axs[1,0].plot(cam_1[:,0], label='x_c_1')
axs[1,0].set_ylim([-2,2])
axs[1,1].plot(cam_1[:,1], label='y_c_1')
axs[1,1].set_ylim([-2,2])
axs[1,2].plot(cam_1[:,2], label='z_c_1')
axs[1,2].set_ylim([-2,2])
axs[2,0].plot(cam_2[:,0], label='x_c_2')
axs[2,0].set_ylim([-2,2])
axs[2,1].plot(cam_2[:,1], label='y_c_2')
axs[2,1].set_ylim([-2,2])
axs[2,2].plot(cam_2[:,2], label='z_c_2')
axs[2,2].set_ylim([-2,2])
axs[3,0].plot(cam_3[:,0], label='x_c_3')
axs[3,0].set_ylim([-2,2])
axs[3,1].plot(cam_3[:,1], label='y_c_3')
axs[3,1].set_ylim([-2,2])
axs[3,2].plot(cam_3[:,2], label='z_c_3')
axs[3,2].set_ylim([-2,2])


plt.show()