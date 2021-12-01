from dv import NetworkEventInput
import multiprocessing as mp
import time
import numpy as np
import signal
import pdb
import cv2
import sys



class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


# python3 one_cam_visuals.py <cam_id>

if __name__ == '__main__':
    
  global killer, mat

  killer = GracefulKiller()


  # Get Arguments
  cam_id = int(sys.argv[1])
  print(cam_id)


  delta_t = 0.001 #1ms
  fps = 20
  max_sfc = 1/delta_t/fps # 40 for 25fps and 1000 sb/sec
  
  port_nb = 7770 + cam_id




  t_sfc = time.time()
  t_evc = t_sfc
  ev_count = 0
  sfc = 0 # sub-frame counter

  mat = np.zeros((480,640))
  with NetworkEventInput(address='172.16.222.46', port=port_nb) as i:
      for event in i:
          t1 = time.time()
          
          mat[event.y, event.x] += 1
          ev_count += 1

          if killer.kill_now:
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

                mat = mat*0.0

              t_sfc = t_current

              if t_current - t_evc >= 1:
                print("%d events per sec" %(ev_count))
                ev_count = 0
                t_evc = t_current
              # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
        


  cv2.destroyAllWindows()

  print("\n\n\n Streaming has been stopped by user :) ")

