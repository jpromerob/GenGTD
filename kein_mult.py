from dv import NetworkEventInput
import multiprocessing as mp
import torch
import time
import numpy as np
import signal
from matplotlib import pyplot as plt
from matplotlib import animation
import pdb
import threading as th
import queue




class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True






def get_events(cam_id, q1):

    global killer
    
    mat = np.zeros((640, 480))


    fps = 25
    delta_t = 1/fps
    port_nb = 7770 + cam_id

    q1.put_nowait(1)

    t_start = time.time()
    count = 0
    with NetworkEventInput(address='127.0.0.1', port=port_nb) as i:
        for event in i:
            if killer.kill_now:
                break
            if time.time() >= t_start + delta_t:
                # pdb.set_trace()

                # plt.imshow(mat[:,:,cam_id-1])
                # plt.show()
                # q1.put_nowait(count)
                t_start = time.time()
                mat = np.zeros((640,480))
                count = 0
                # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
                
            else:
                mat[event.x, event.y] += 1
                count += 1
            


# nx = 150
# ny = 50

# fig = plt.figure()
# data = np.zeros((nx, ny))
# im = plt.imshow(data, cmap='gist_gray_r', vmin=0, vmax=1)

# def init():
#     im.set_data(np.zeros((nx, ny)))

# def animate(i):
#     xi = i // ny
#     yi = i % ny
#     data[xi, yi] = 1
#     im.set_data(data)
#     return im

# anim = animation.FuncAnimation(fig, animate, init_func=init, frames=nx * ny,
#                                interval=50)

# plt.show()




def init():
    im.set_data(np.zeros((640,480)))

def animate(i):
    im.set_data(mat)
    return im


if __name__ == '__main__':
    
    global killer

    killer = GracefulKiller()

    
    mat = np.zeros((640, 480))

    fig = plt.figure()
    
    im = plt.imshow(mat, cmap='gist_gray_r', vmin=0, vmax=1)

    cam_id = 1

    fps = 25
    delta_t = 1/fps
    port_nb = 7770 + cam_id




    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=640*480,
                                interval=50)

    plt.show(block=False)

    t_start = time.time()
    count = 0
    with NetworkEventInput(address='127.0.0.1', port=port_nb) as i:
        for event in i:
            if killer.kill_now:
                break
            if time.time() >= t_start + delta_t:
                # plt.imshow(mat[:,:,cam_id-1])
                # plt.show()
                t_start = time.time()
                mat = np.zeros((640,480))
                count = 0
                # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
                
            else:
                mat[event.x, event.y] += 1
                count += 1


    print("\n\n\n Streaming has been stopped by user :) ")



