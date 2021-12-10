
# coding: utf-8
from __future__ import print_function

'''
This script is used to save object pose during dataset recordings.
'''

import argparse
import time
import attr
import natnet
import csv
import pdb
import sys
from datetime import datetime

global f 

@attr.s
class ClientApp(object):

    _client = attr.ib() 

    @classmethod
    def connect(cls):
        client = natnet.Client.connect()
        if client is None:
            return None
        return cls(client)

    def run(self):
        self._client.set_callback(self.callback)
        self._client.spin()

    def callback(self, rigid_bodies, markers, timing):

        global f, asset_id
        
        for b in rigid_bodies:
            if b.id_ == asset_id:

                line = '{:.6f},{: 3.6f},{: 3.6f},{: 3.6f}\n'.format(time.time(), b.position[0], b.position[1], b.position[2])
                f.write(line)

def main():    

    print("Writing poses to *.csv")
    try:
        app = ClientApp.connect()
        app.run()
    except natnet.DiscoveryError as e:
        print('Error:', e)


if __name__ == '__main__':


    global f, asset_id

    try:
        asset_id = int(sys.argv[1]) # The id of the asset (hammer, stimulus, camhat) in optitrack
        version = int(sys.argv[2]) # Version of dataset (the one to be created with the poses saved here)

        if asset_id == 1:
            print("Showing hammer poses")
        elif asset_id == 2:
            print("Showing camhat poses")
        elif asset_id == 3:
            print("Showing stimulus poses")
        else:
            print("Wrong asset_id (Hammer: 1, Camhat: 2, Stimulus: 3)")
            quit()

        time.sleep(3)

    except:
        print("Usage: python3 pose_to_csv.py <asset_id> <version>")
        quit()

    now = datetime.now() # current date and time
    date_time = now.strftime("%Y-%m-%d_%Hh%M")
    print("date and time:",date_time)

    path = '/home/juan/CameraSetup/Recordings_3cams'
    pose_file = path + "/poses_v" + str(version) + ".csv"

    f = open(pose_file, 'a') 
    main()
    f.close()

    print("Pose dataset created :)")

