from multiprocessing import Process, Lock

class pose:
    def __init__(self, x=0, y=0,z=0,alpha=0, beta=0, gamma=0):
        self.x = x
        self.y = y
        self.z = z
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

mutex = Lock()


# mutex.acquire()
# try:
#     print('Do some stuff')
# finally:
#     mutex.release()

def getCam(cam_id):
    print("Cam %d" %(cam_id))

def update_pose():
    a = 1


if __name__ == '__main__':
    
    c1 = Process(target = getCam, args = (1,))
    c2 = Process(target = getCam, args = (2,))
    c3 = Process(target = getCam, args = (3,))

    c1.start()
    c2.start()
    c3.start()

    c1.join()
    c2.join()
    c3.join()

    print("C'est fini")

