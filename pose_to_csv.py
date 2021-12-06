
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

        global f
        
        for b in rigid_bodies:
            if b.id_ == 1:

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


    now = datetime.now() # current date and time
    date_time = now.strftime("%Y-%m-%d_%Hh%M")
    print("date and time:",date_time)

    global f
    f = open('gtd_' + date_time+'.csv', 'a') #gtd: ground truth data
    main()
    f.close()

    print("Pose dataset created :)")

