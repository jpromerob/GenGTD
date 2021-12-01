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


def visualize(cam_id):

  global mat

  # while not killer.kill_now:
  #   cv2.imshow('frame', mat)
  #   cv2.waitKey(1)
  # cv2.destroyAllWindows()


if __name__ == '__main__':
    
  global killer, mat

  killer = GracefulKiller()

  cam_id = 1

  mat = np.zeros((480,640))

  delta_t = 0.010 #1ms
  fps = 50
  max_sfc = 1/delta_t/fps # 40 fo 25fps and 1000 sb/sec
  
  port_nb = 7770 + cam_id

  v1 = mp.Process(target=visualize, args=(cam_id,))
  v1.start()




  t_sfc = time.time()
  t_evc = t_sfc
  ev_count = 0
  sfc = 0 # sub-frame counter

  with NetworkEventInput(address='172.16.222.46', port=port_nb) as i:
      for event in i:
          t1 = time.time()
          
          mat[event.y, event.x] += 1
          ev_count += 1

          if killer.kill_now:
              print("Killing stuff")
              break

          t_current = time.time() 

          # Check if new subfram needs to be started
          if t_current - t_sfc >= (delta_t):
              sfc += 1

              # Check if visual frame needs to be shown
              if sfc >= max_sfc:
                
                
                cv2.imshow("frame", mat)
                cv2.waitKey(1)      
                sfc = 0      

              mat = mat*0.5

              t_sfc = t_current

              if t_current - t_evc >= 1:
                # print("%d events per sec" %(ev_count))
                ev_count = 0
                t_evc = t_current
              # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
        


  v1.join()

  cv2.destroyAllWindows()

  print("\n\n\n Streaming has been stopped by user :) ")

