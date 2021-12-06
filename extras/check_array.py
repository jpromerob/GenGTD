import multiprocessing as mp
import time
import numpy as np

def f(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]*2
        # print(a[:])


def g(n, a):
    n.value = n.value+1
    for i in range(len(a)):
        a[i] = -a[i]/3
        # print(a[:])

if __name__ == '__main__':
    num = mp.Value('d', 0.0)
    arr = mp.Array('d', np.random.rand(4*3,1))

    p1 = mp.Process(target=f, args=(num, arr))
    p2 = mp.Process(target=g, args=(num, arr))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    p1.join()

    print(num.value)
    print(arr[:])