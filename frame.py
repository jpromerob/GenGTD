from dv import NetworkFrameInput
import cv2

cam_id = 1
port_nb = 7770 + cam_id

with NetworkFrameInput(address='172.16.222.46', port=port_nb) as i:
    for frame in i:
        print(frame.position)
        print(dir(frame.position))
        break
        # cv2.imshow('out', frame.image)
        # cv2.waitKey(1)
