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

def clear_fast(cam_shape, fast_arr):
  fast_arr[:] = np.zeros(np.prod(cam_shape))

def refresh(cam_shape, fast_arr, ready):

  # process that will handle cleaning of pixel matrix
  p_clean_f = mp.Process()

  delta_t = 0.003 #1ms
  fps = 30
  max_sfc = 1/delta_t/fps # 40 for 25fps and 1000 sb/sec
  
  t_sfc = time.time() # time corresponding to current sub-frame
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

      # Clear sub-frame
      if not p_clean_f.is_alive():
        p_clean_f = mp.Process(target=clear_fast, args=(cam_shape, fast_arr))
        p_clean_f.start()
 
      t_sfc = t_current

      #HERE: the array is ready


def insert_events(buff, fast_arr, slow_arr):
  for idx in range(buff.shape[0]):
      fast_arr[buff[idx][2]*640 + buff[idx][1]] += 1
      slow_arr[buff[idx][2]*640 + buff[idx][1]] += 1


def receive_events(cam_id, fast_arr, slow_arr):
  
  port_nb = 7770 + cam_id

  nb_proc = 10
  p_list = []

  with NetworkNumpyEventPacketInput(address='172.16.222.46', port=port_nb) as i:
    for buff in i:
      if killer.kill_now:
          break
      # print(buffer.shape)
      if len(p_list) < nb_proc:
        p_list.append(mp.Process(target=insert_events, args=(buff, fast_arr, slow_arr)))
        idx = len(p_list)-1
      else:
        if idx < len(p_list)-1:
          idx += 1
        else:
          idx = 0

        if not p_list[idx].is_alive():
          p_list[idx] = mp.Process(target=insert_events, args=(buff, fast_arr, slow_arr))
          p_list[idx].start()


def visualize(cam_shape, slow_arr, ready):

  pixmat = np.frombuffer(slow_arr.get_obj(), dtype="d").reshape(cam_shape)

  while not killer.kill_now:
    
    if ready.value == 1:

      cv2.imshow("frame", pixmat)
      cv2.waitKey(1) 
      ready.value = 0
        
      slow_arr[:] = np.zeros(np.prod(cam_shape))


if __name__ == '__main__':
    
  global killer


  try:
    cam_id = int(sys.argv[1])
  except:
    print("Try 'python3 tcp_event_handler.py <cam_id>'")
    quit()
  
  print("# of processors available: %d" %(mp.cpu_count()))

  killer = GracefulKiller()

  cam_shape = (480,640)

  ready = mp.Value('i', 0)
  fast_arr = mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock())
  slow_arr = mp.Array('d', np.zeros((np.prod(cam_shape),1)), lock=mp.Lock())

  p1 = mp.Process(target=receive_events, args=(cam_id, fast_arr, slow_arr))
  c1 = mp.Process(target=refresh, args=(cam_shape, fast_arr, ready))
  v1 = mp.Process(target=visualize, args=(cam_shape, slow_arr, ready))
 



  p1.start()
  c1.start()
  v1.start()

    

  p1.join()
  c1.join()
  v1.join()

  cv2.destroyAllWindows()


  print("\n\n\n Streaming has been stopped by user :) ")

