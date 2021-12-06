from dv import NetworkEventInput
import multiprocessing as mp
import time
import numpy as np
import signal
from matplotlib import pyplot as plt
from matplotlib import animation
import pdb
import cv2



class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


def get_events(cam_id):

    global killer


    fps = 100
    delta_t = 1/fps
    port_nb = 7770 + cam_id


    t_start = time.time()
    count = 0
    with NetworkEventInput(address='172.16.222.46', port=port_nb) as i:
        for event in i:
            if killer.kill_now:
                break
            if time.time() - t_start >= delta_t:
                t_start = time.time()
                # print(count/delta_t)
                count = 0
                # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
            count += 1


            



if __name__ == '__main__':
    
    global killer

    killer = GracefulKiller()

    c1 = mp.Process(target = get_events, args = (1,))
    # c2 = mp.Process(target = get_events, args = (2,))
    # c3 = mp.Process(target = get_events, args = (3,))

    c1.start()
    # c2.start()
    # c3.start()

    c1.join()
    # c2.join()
    # c3.join()


    print("\n\n\n Streaming has been stopped by user :) ")

