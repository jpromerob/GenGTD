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

def get_events(cam_id, cam_shape, arr):


  delta_t = 0.001 #1ms
  fps = 20
  max_sfc = 1/delta_t/fps # 40 for 25fps and 1000 sb/sec
  
  port_nb = 7770 + cam_id




  t_sfc = time.time()
  t_evc = t_sfc
  ev_count = 0
  sfc = 0 # sub-frame counter

  mat = np.zeros(cam_shape)
  with NetworkEventInput(address='172.16.222.46', port=port_nb) as i:
      for event in i:

          if killer.kill_now:
              break

          t1 = time.time()
          
          mat[event.y, event.x] += 1

          ev_count += 1


          t_current = time.time() 

          # Check if new subfram needs to be started
          if t_current - t_sfc >= (delta_t):
              sfc += 1

              # Check if visual frame needs to be shown
              if sfc >= max_sfc:
                
                arr[:] = mat.reshape((np.prod(cam_shape),1))
                # tam = np.array(arr).reshape((480,640))
                # cv2.imshow("frame", mat)
                # cv2.waitKey(1)  
                sfc = 0      

                mat = mat*0.1

              t_sfc = t_current

              if t_current - t_evc >= 1:
                print("%d events per sec" %(ev_count))
                ev_count = 0
                t_evc = t_current
              # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
          
        

def visualize(cam_id, cam_shape, arr):

  while not killer.kill_now:
    tam = np.array(arr).reshape(cam_shape)
    cv2.imshow("frame", tam)
    cv2.waitKey(1) 

if __name__ == '__main__':
    
  global killer

  print(mp.cpu_count())

  killer = GracefulKiller()

  cam_shape = (480,640)

  arr = mp.Array('d', np.zeros((np.prod(cam_shape),1)))

  p1 = mp.Process(target=get_events, args=(1, cam_shape, arr,))
  v1 = mp.Process(target=visualize, args=(1, cam_shape, arr,))



  p1.start()
  v1.start()

    

  p1.join()
  v1.join()

  cv2.destroyAllWindows()


  print("\n\n\n Streaming has been stopped by user :) ")

