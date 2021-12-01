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

def get_events(cam_id, cam_shape, arr, rdy):


  delta_t = 0.001 #1ms
  fps = 50
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
      arr[event.y*640 + event.x] += 1

      ev_count += 1


      t_current = time.time() 

      # Check if new subfram needs to be started
      if t_current - t_sfc >= (delta_t):
        sfc += 1

        # Check if visual frame needs to be shown
        if sfc >= max_sfc:
          rdy.value = 1

          sfc = 0      

          mat = mat*0.1
          arr[:] = np.zeros(np.prod(cam_shape))

        t_sfc = t_current

        if t_current - t_evc >= 1:
          print("%d events per sec" %(ev_count))
          ev_count = 0
          t_evc = t_current
        # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
          
        

def visualize(cam_id, cam_shape, tam, rdy):

  while not killer.kill_now:
    # tam = np.array(arr).reshape(cam_shape)
    if rdy.value == 1:
      cv2.imshow("frame", tam)
      cv2.waitKey(1) 
      rdy.value = 0
    

if __name__ == '__main__':
    
  global killer

  rdy = False

  print(mp.cpu_count())

  killer = GracefulKiller()

  cam_shape = (480,640)

  rdy_1 = mp.Value('i', 0)
  arr_1 = mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock())
  tam_1 = np.frombuffer(arr_1.get_obj(), dtype="d").reshape(cam_shape)
  p1 = mp.Process(target=get_events, args=(1, cam_shape, arr_1, rdy_1))
  v1 = mp.Process(target=visualize, args=(1, cam_shape, tam_1, rdy_1))

  rdy_2 = mp.Value('i', 0)
  arr_2 = mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock())
  tam_2 = np.frombuffer(arr_2.get_obj(), dtype="d").reshape(cam_shape)
  p2 = mp.Process(target=get_events, args=(2, cam_shape, arr_2, rdy_2))
  v2 = mp.Process(target=visualize, args=(2, cam_shape, tam_2, rdy_2))

  rdy_3 = mp.Value('i', 0)
  arr_3 = mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock())
  tam_3 = np.frombuffer(arr_3.get_obj(), dtype="d").reshape(cam_shape)
  p3 = mp.Process(target=get_events, args=(3, cam_shape, arr_3, rdy_3))
  v3 = mp.Process(target=visualize, args=(3, cam_shape, tam_3, rdy_3))




  p1.start()
  v1.start()
  p2.start()
  v2.start()
  p3.start()
  v3.start()

    

  p1.join()
  v1.join()
  p2.join()
  v2.join()
  p3.join()
  v1.join()

  cv2.destroyAllWindows()


  print("\n\n\n Streaming has been stopped by user :) ")

