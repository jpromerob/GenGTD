from dv import NetworkEventInput, NetworkNumpyEventPacketInput
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


def cleaner(cam_id, cam_shape, arr, ready):

  delta_t = 0.001 #1ms
  fps = 50
  max_sfc = 1/delta_t/fps # 40 for 25fps and 1000 sb/sec
  
  t_sfc = time.time() 
  sfc = 0 # sub-frame counter

  while not killer.kill_now:

    t_current = time.time() 
    # Check if new subfram needs to be started
    if t_current - t_sfc >= (delta_t):
      sfc += 1

      # Check if visual frame needs to be shown
      if sfc >= max_sfc:
        ready.value = 1

        sfc = 0      

        arr[:] = np.zeros(np.prod(cam_shape))

      t_sfc = t_current


def update_matrix(buff, arr):
  for idx in range(buff.shape[0]):
      arr[buff[idx][2]*640 + buff[idx][1]] += 1
    # print("      %ld : (%d,%d)" %(buff[idx][0], buff[idx][1], buff[idx][2]))
    # buffer[idx][0]
    # buffer[idx][1]
    # buffer[idx][2]


def get_events(cam_id, cam_shape, arr, ready):


  delta_t = 0.001 #1ms
  fps = 50
  max_sfc = 1/delta_t/fps # 40 for 25fps and 1000 sb/sec
  
  port_nb = 7770 + cam_id

  t_sfc = time.time()
  t_evc = t_sfc
  ev_count = 0
  sfc = 0 # sub-frame counter

  mat = np.zeros(cam_shape)

  nb_proc = 10
  p_list = []

  with NetworkNumpyEventPacketInput(address='172.16.222.46', port=port_nb) as i:
    for buff in i:
      if killer.kill_now:
          break
      # print(buffer.shape)
      if len(p_list) < nb_proc:
        p_list.append(mp.Process(target=update_matrix, args=(buff, arr)))
        idx = len(p_list)-1
      else:
        if idx < len(p_list)-1:
          idx += 1
          p_list[idx].join()
        else:
          idx = 0
          p_list[idx].join()

        p_list[idx] = mp.Process(target=update_matrix, args=(buff, arr))
      
      p_list[idx].start()


def visualize(cam_id, cam_shape, tam, ready):

  while not killer.kill_now:
    # tam = np.array(arr).reshape(cam_shape)
    if ready.value == 1:

      cv2.imshow("frame", tam)
      cv2.waitKey(1) 
      ready.value = 0
    

if __name__ == '__main__':
    
  global killer

  try:
    cam_id = int(sys.argv[1])
  except:
    quit()
  


  ready = False

  print(mp.cpu_count())

  killer = GracefulKiller()

  cam_shape = (480,640)

  ready = mp.Value('i', 0)
  arr = mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock())
  tam = np.frombuffer(arr.get_obj(), dtype="d").reshape(cam_shape)

  p1 = mp.Process(target=get_events, args=(cam_id, cam_shape, arr, ready))
  c1 = mp.Process(target=cleaner, args=(cam_id, cam_shape, arr, ready))
  v1 = mp.Process(target=visualize, args=(cam_id, cam_shape, tam, ready))



  p1.start()
  c1.start()
  v1.start()

    

  p1.join()
  c1.join()
  v1.join()

  cv2.destroyAllWindows()


  print("\n\n\n Streaming has been stopped by user :) ")

