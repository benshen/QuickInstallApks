#!/usr/bin/env python
# by Benshen Lee 20150422

import os
import subprocess
import glob
import shlex
import time
import Queue
import threading


APP_FILTER = "*.apk"

DEVICE_IDS = [

]


pendingQueueDict = {}
workingProcessDict = {}
MAX_WORKING_PROCESS = 10  # you can set the size to the proper value is 10


def beep():
    print '\7' * 5


def worker(devid):
    print 'worker - devid: %s\n' % devid

    pendingQueue = pendingQueueDict[devid]
    workingProcess = workingProcessDict[devid]

    while not pendingQueue.empty():
        # check the working process is done or not, if done then remove it
        # this action can be done by another new thread!!!
        # need to improve in the futhure
        for k, v in workingProcess.items():
            if v.poll() == 0:
                workingProcess.pop(k)
                # print '[%s] remove working process: %s' % (devid, k)

        # show the current working process size
        currWorkingProcessSize = len(workingProcess)
        # print '[%s] working process size: %s' % (devid,
        # currWorkingProcessSize)

        # if working process is full, then have to wait...
        if currWorkingProcessSize == MAX_WORKING_PROCESS:
            # print '[%s] working process is full, have to wait...' % devid
            time.sleep(1)
            continue

        for i in range(MAX_WORKING_PROCESS - currWorkingProcessSize):
            # pop from pending queue and push into working process
            try:
                app = pendingQueue.get(False)
            except:
                # pendingQueue is empty! return.
                return

            # print '[%s] start to pop from pending queue: %s' % (devid, app)

            # start process
            cmd = "adb -s " + devid + " install " + app + " > NUL"
            p = subprocess.Popen(cmd, shell=True)

            # add process to working process
            workingProcess['%s' % app] = p
            print '[%s] add to working process queue: %s' % (devid, app)
            time.sleep(0.5)
            # print 'process is %s' % str(p)


def main():
    global DEVICE_IDS

    try:
        appDir = os.sys.argv[1]
    except:
        print "please input your app directory path!"
        exit()

    if len(DEVICE_IDS) == 0:
        cmd = 'adb devices'
        ret = subprocess.check_output(cmd)

        devlist = ret.strip().split('\n')[1:]
        for dev in devlist:
            try:
                DEVICE_IDS.append(dev.split('\t')[0])
            except:
                pass

    appList = glob.glob(appDir + os.sep + APP_FILTER)
    appCount = len(appList)

    print "*** Total App Count: %d ***\n" % appCount
    start = time.time()

    # init pending queue and working process poll
    for devid in DEVICE_IDS:
        pendingQueueDict[devid] = Queue.Queue()
        workingProcessDict[devid] = dict()

    # setup pending queue
    for app in appList:
        for devid in DEVICE_IDS:
            q = pendingQueueDict[devid]
            q.put(app)

    # run thread
    threads = []
    for devid in DEVICE_IDS:
        print 'start thread to deal with devid: %s' % devid
        t = threading.Thread(target=worker, args=(devid,))
        threads.append(t)
        t.start()

    time.sleep(5)
    # waiting for thread done
    for t in threads:
        t.join()

    end = time.time()
    print 'Job done! \nElapsed: %s sec' % (end - start)
    beep()

if __name__ == "__main__":
    main()
