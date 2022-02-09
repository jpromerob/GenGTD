from dv import NetworkEventInput
import multiprocessing as mp

import multiprocessing 
import time
import numpy as np
import signal
import pdb
import math
import cv2
import sys



""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float)]


class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True



def createpixel(cam_shape, LED_queue):

    global killer

    i = 0
    while not killer.kill_now:

        i+= 1
        x = int((math.cos(i*math.pi/180)+1)/2*(cam_shape[1]-1))
        y = int((math.sin(i*math.pi/180)+1)/2*(cam_shape[0]-1))
        LED_queue.put([x, y])
    
    print("Bye bye create pixel")

def snn_main(snn_queue):

    global snn_xyz

    PORT = 2600
    server_addr = ("172.16.222.46", PORT)
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    try:
        # bind the server socket and listen
        ssock.bind(server_addr)
        print("Bind done")
        ssock.listen(3)
        print("Server listening on port {:d}".format(PORT))

        # while True:
        csock, client_address = ssock.accept()
        print("Accepted connection from {:s}".format(client_address[0]))

        buff = csock.recv(512)
        while buff:
            payload_in = Payload.from_buffer_copy(buff) 
            snn_xyz = [payload_in.x, payload_in.y, payload_in.z]
            snn_queue.put([payload_in.x, payload_in.y, payload_in.z])
            buff = csock.recv(512)

            if killer.kill_now:
                break
        print("Closing connection to client")
        print("----------------------------")
        csock.close()

    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    except KeyboardInterrupt:
        ssock.close()
    finally:
        print("Closing socket")
        
    print("c'est fini snn_main")



def pixel_main(opt_queue, snn_queue):

    global killer


    snn_xyz = [0.0,0.0,0.0]

    start_time = time.time()
    while not killer.kill_now:

        
        if not snn_queue.empty():
            snn_xyz = snn_queue.get(False)

        end_time = time.time()

        time_elapsed = (end_time - start_time)
        if time_elapsed >= 1/100:
            start_time = time.time()
            x = snn_xyz[1]
            y = snn_xyz[2]
            

def visualize(cam_shape, LED_queue):

    global killer

    i = 0
    while not killer.kill_now:

        image = np.zeros(cam_shape)
        datum = LED_queue.get()
        x = datum[0]
        y = datum[1]
        image[y,x] = 255
        for i in range(6):
            if x+i <= cam_shape[1]-1:
                image[y,x+i] = 255
            if x-i > 0:
                image[y,x-i] = 255
            if y+i <= cam_shape[0]-1:
                image[y+i,x] = 255
            if y-i > 0:
                image[y-i,x] = 255


        cv2.imshow("frame", image)
        cv2.waitKey(5) 

    print("Bye bye visualize")
    

if __name__ == '__main__':
    
    global killer

    #   try:
    #     cam_id = int(sys.argv[1])
    #   except:
    #     quit()




    killer = GracefulKiller()

    cam_shape = (480,640)


    LED_queue = multiprocessing.Queue()
    v1 = mp.Process(target=visualize, args=(cam_shape,LED_queue))
    p1 = mp.Process(target=createpixel, args=(cam_shape,LED_queue))



    v1.start()
    p1.start()


    # v1.join()
    # p1.join()

    v1.join()
    p1.join()


    cv2.destroyAllWindows()

    quit()
    print("\n\n\n Streaming has been stopped by user :) ")
    # quit()

