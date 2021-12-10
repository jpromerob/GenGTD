import os
import sys
import time

if __name__ == '__main__':

    try:
        version = int(sys.argv[1]) # Version of new dataset

        print("Renaming recordings to create v%d of the dataset" %(version))

        time.sleep(3)

    except:
        print("Usage: python3 renamer.py <version>")
        quit()

    for i in [1,2,3]:
        path = '/home/juan/CameraSetup/Recordings_3cams/cam' + str(i)

        files = os.listdir(path)

        for f in files:

            if "2021" in f: 
                old_name = path + '/' + f
                new_name = path + '/' + 'cam' + str(i) + '_v' + str(version) + '.aedat4'
                print(old_name)
                print(new_name)
                os.rename(old_name, new_name)
