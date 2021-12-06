from dv import NetworkEventInput
import multiprocessing as mp
import time
import numpy as np
import signal
import pdb
import cv2
import sys
import socket

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

  with NetworkEventInput(address='172.16.222.46', port=port_nb) as i:
    for event in i:

      if killer.kill_now:
          break

      ev_count += 1
      
      t1 = time.time()
      
      arr[event.y*640 + event.x] += 1



      t_current = time.time() 

      # Check if new subfram needs to be started
      if t_current - t_sfc >= (delta_t):
        sfc += 1

        # Check if visual frame needs to be shown
        if sfc >= max_sfc:
          rdy.value = 1

          sfc = 0      

          arr[:] = np.zeros(np.prod(cam_shape))

        t_sfc = t_current

        if t_current - t_evc >= 1:
          # print("%d events per sec" %(ev_count))
          ev_count = 0
          t_evc = t_current
        # print("Cam %d @ %ld : (%d,%d) [%d]" %(cam_id, event.timestamp, event.x, event.y, event.polarity))
          
        

def visualize(cam_id, img, rdy):

  while not killer.kill_now:
    if rdy.value == 1:
      cv2.imshow("Camera #" + str(cam_id), img)
      cv2.waitKey(1) 
      rdy.value = 0
    

if __name__ == '__main__':
    
  global killer


  killer = GracefulKiller()

  cam_shape = (480,640)

  rdy = []
  arr = []
  img = []
  pro = []
  vis = []

  for i in range(3):
    cam_id = i+1
    rdy.append(mp.Value('i', 0))
    arr.append(mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock()))
    img.append(np.frombuffer(arr[i].get_obj(), dtype="d").reshape(cam_shape))
    pro.append(mp.Process(target=get_events, args=(cam_id, cam_shape, arr[i], rdy[i])))
    vis.append(mp.Process(target=visualize, args=(cam_id, img[i], rdy[i])))


  for i in range(3):
    pro[i].start()
    vis[i].start()

    

  for i in range(3):
    pro[i].join()
    vis[i].join()

  cv2.destroyAllWindows()


  print("\n\n\n Streaming has been stopped by user :) ")

