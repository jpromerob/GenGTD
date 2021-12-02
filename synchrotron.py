import sys, getopt
import pdb
import time
import cv2 as cv
import matplotlib.pyplot as plt
from dv import AedatFile
import numpy as np
from numpy import genfromtxt



    
'''
This code produces 1 image out of events every 1/<fps>ms
Images are ignored when less than <activity>% of the pixels are inactive 
Among the used images, one will be stored after visual/manual inspection
The image to be stored needs to be evidently affected by lens distortion
The distorted image is necesary to check distortion maps
'''


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


    for i in range(3):
        cam_id = i+1
        my_dpi = 40
        x_max = 640
        y_max = 480

        screen = np.zeros((x_max, y_max),dtype=int)

        inputfile = path + "/cam"+ str(cam_id)+"/cam"+ str(cam_id)+ "_v" + str(version) + ".aedat4"

        start = time.time()

        ev_count = 0
        next_print = 0
        sec_count = 0



        f = open("all_data_cam" + str(cam_id) + "_v" + str(version) + ".csv", 'a')
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

                # print('{:.0f} : ({: 3.6f}, {: 3.6f}, {: 3.6f})'.format(cp[0], cp[1], cp[2], cp[3]))
                # print('{:d} : ({: d},{: d})'.format(t, x, y))
        f.close()
            

        stop = time.time() 

        elapsed = stop - start
        print("Parser took: " + str(elapsed-1) + " seconds.")
        