from numpy import genfromtxt
import numpy as np
import math
import sys
import matplotlib.pyplot as plt


if __name__ == '__main__':

    filename = sys.argv[1]

    if "rec_px_opt_" in filename:
        d_source = "OPT"
        date = filename.replace("rec_px_opt_", "")
    elif "rec_px_snn_" in filename:
        d_source = "SNN"
        date = filename.replace("rec_px_snn_"), ""
    else:
        print("Wrong file! ... try rec_px_<opt|snn>_<YYYYmmdd_HHMM>.csv")
        quit()
    date = date.replace(".csv", "")

    print(date)

    pixel = genfromtxt(filename, delimiter=',')
    
    # print(len(opt_xyz))

    l = len(pixel)

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
        if pixel[i, 0] == 1:
            x_1[idx_1] = pixel[i, 1]
            y_1[idx_1] = pixel[i, 2]
            idx_1 += 1
        if pixel[i, 0] == 2:
            x_2[idx_2] = pixel[i, 1]
            y_2[idx_2] = pixel[i, 2]
            idx_2 += 1
        if pixel[i, 0] == 3:
            x_3[idx_3] = pixel[i, 1]
            y_3[idx_3] = pixel[i, 2]
            idx_3 += 1


    

    fig, axs = plt.subplots(3,3)
    fig.suptitle(d_source + ' Output (in pixel space) \n @' + date)
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


