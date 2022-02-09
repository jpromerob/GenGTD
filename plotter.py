from numpy import genfromtxt
import numpy as np
import math
import sys
import matplotlib.pyplot as plt


if __name__ == '__main__':

    filename = sys.argv[1]

    csv_data = genfromtxt(filename, delimiter=',')
    opt_xyz = csv_data[:,0:3]
    snn_xyz = csv_data[:,3:6]
    
    # print(len(opt_xyz))

    distance = np.zeros(opt_xyz.shape[0])


    for i in range(len(distance)):

        d_x = opt_xyz[i, 0]-snn_xyz[i, 0]
        d_y = opt_xyz[i, 1]-snn_xyz[i, 1]
        d_z = opt_xyz[i, 2]-snn_xyz[i, 2]

        distance[i] = math.sqrt(d_x*d_x + d_y*d_y + d_z*d_z)


    print(distance)

    fig, axs = plt.subplots(4)
    fig.suptitle('Optitrack vs SNN/Merging')
    axs[0].plot(opt_xyz[:,0], label='Opt')
    axs[0].plot(snn_xyz[:,0], label='SNN')
    axs[0].set_ylabel('x\n(towards/away-from hugin)')
    axs[0].set_ylim([-0.8,1.5])
    axs[0].legend()
    axs[1].plot(opt_xyz[:,1], label='Opt')
    axs[1].plot(snn_xyz[:,1], label='SNN')
    axs[1].set_ylabel('y\n(up/down)')
    axs[1].set_ylim([-0.8,1.5])
    axs[1].legend()
    axs[2].plot(opt_xyz[:,2], label='Opt')
    axs[2].plot(snn_xyz[:,2], label='SNN')
    axs[2].set_ylabel('z\n(away-from/towards munin)')
    axs[2].set_ylim([-0.8,1.5])
    axs[2].legend()
    axs[3].plot(distance, label='delta', color='g')
    axs[3].set_ylabel('euclidean distance')
    axs[3].set_ylim([-0.8,1.5])
    axs[3].legend()

    plt.show()


