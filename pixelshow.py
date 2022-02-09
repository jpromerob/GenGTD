from numpy import genfromtxt
import numpy as np
import math
import sys
import matplotlib.pyplot as plt


if __name__ == '__main__':

    filename = sys.argv[1]

    csv_data = genfromtxt(filename, delimiter=',')
    snn_xyz = csv_data[:,3:6]
    
    # print(len(opt_xyz))

    l = len(snn_xyz)

    x_1 = np.zeros((l,1))
    x_2 = np.zeros((l,1))
    x_3 = np.zeros((l,1))
    y_1 = np.zeros((l,1))
    y_2 = np.zeros((l,1))
    y_3 = np.zeros((l,1))

    idx_1 = 0
    idx_2 = 0
    idx_3 = 0
    for i in range(l):
        if snn_xyz[i, 0] == 1:
            x_1[idx_1] = snn_xyz[i, 1]
            y_1[idx_1] = snn_xyz[i, 2]
            idx_1 += 1
        if snn_xyz[i, 0] == 2:
            x_2[idx_2] = snn_xyz[i, 1]
            y_2[idx_2] = snn_xyz[i, 2]
            idx_2 += 1
        if snn_xyz[i, 0] == 3:
            x_3[idx_3] = snn_xyz[i, 1]
            y_3[idx_3] = snn_xyz[i, 2]
            idx_3 += 1




    fig, axs = plt.subplots(3,3)
    fig.suptitle('SNN Output (in pixel space)')
    axs[0,0].plot(x_1)
    axs[0,0].set_ylabel('x')
    axs[0,0].set_ylim([0,640])
    # axs[0,0].legend()
    axs[0,0].set_title('Cam #1 - x')
    axs[0,1].plot(x_2)
    axs[0,1].set_ylabel('x')
    axs[0,1].set_ylim([0,640])
    # axs[0,1].legend()
    axs[0,1].set_title('Cam #2 - x')
    axs[0,2].plot(x_3)
    axs[0,2].set_ylabel('x')
    axs[0,2].set_ylim([0,640])
    # axs[0,2].legend()
    axs[0,2].set_title('Cam #3 - x')

    axs[1,0].plot(y_1)
    axs[1,0].set_ylabel('y')
    axs[1,0].set_ylim([0,480])
    # axs[1,0].legend()
    axs[1,0].set_title('Cam #1 - y')
    axs[1,1].plot(y_2)
    axs[1,1].set_ylabel('y')
    axs[1,1].set_ylim([0,480])
    # axs[1,1].legend()
    axs[1,1].set_title('Cam #2 - y')
    axs[1,2].plot(y_3)
    axs[1,2].set_ylabel('y')
    axs[1,2].set_ylim([0,480])
    # axs[1,2].legend()
    axs[1,2].set_title('Cam #3 - y')



    axs[2,0].plot(x_1, y_1, marker="o")
    axs[2,0].set_xlabel('x')
    axs[2,0].set_ylabel('y')
    axs[2,0].set_xlim([0,640])
    axs[2,0].set_ylim([0,480])
    # axs[2,0].legend()
    axs[2,0].set_title('Cam #1 - x,y')
    axs[2,1].plot(x_2, y_2, marker="o")
    axs[2,1].set_xlabel('x')
    axs[2,1].set_ylabel('y')
    axs[2,1].set_xlim([0,640])
    axs[2,1].set_ylim([0,480])
    # axs[2,1].legend()
    axs[2,1].set_title('Cam #2 - x,y')
    axs[2,2].plot(x_3,y_3, marker="o")
    axs[2,2].set_xlabel('x')
    axs[2,2].set_ylabel('y')
    axs[2,2].set_xlim([0,640])
    axs[2,2].set_ylim([0,480])
    # axs[2,2].legend()
    axs[2,2].set_title('Cam #3 - x,y')
   

    plt.show()


