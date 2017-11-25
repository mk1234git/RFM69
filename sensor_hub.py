#!/usr/bin/env python2

import RFM69
from RFM69registers import *
import datetime
import time
import struct
import sys

test = RFM69.RFM69(RF69_868MHZ, 1, 100, rstPin=26, isRFM69HW=True)
print "class initialized"

if False:
    print "reading all registers"
    results = test.readAllRegs()
    for result in results:
        print result
    
print "Frequency: 0x%06X, %.3f MHz" % (test.getFrf(), test.getFreqMHz())
    
print "Performing rcCalibration"
test.rcCalibration()

print "setting high power"
test.setHighPower(True)
test.setPowerLevel(0);
print "Checking temperature"
print test.readTemperature(0)
print "setting encryption"
#test.encrypt("1234567891011121")
#print "sending blah to 2"
#if test.sendWithRetry(2, "blah", 3, 20):
#    print "ack recieved"
print "reading"

import time
def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


f = open("/var/www/html/temp/temp.txt", "w+")
f.write("start\n")
f.flush()

from collections import namedtuple
dataset = namedtuple('dataset', 'nodeid, rssi, type, cnt, vcc, temp, humi')

lastRx = {} #key is nodeid, value is time

while True:
    test.receiveBegin()
    while not test.receiveDone():
        time.sleep(.5)
        rssi = test.readRSSI()
        #if rssi > -90:
        #    print "%s, %d" % (now(), rssi)
            
    data = "".join([chr(letter) for letter in test.DATA])
    pkttype, cnt, vcc, temp, humi = struct.unpack('BBhhh', data)
    d = dataset(test.SENDERID, test.RSSI, pkttype, cnt, float(vcc)/1000, float(temp)/100, float(humi)/100)
    #print d.temp
    #d.temp /= 100
    #d.humi /= 100
    #d.vcc /= 100
    
    tNow = time.time()
    tLast = lastRx.get(d.nodeid, tNow)
    str = "%s, %d sec, (%d byte), %s" % (now(), tNow - tLast, len(test.DATA), d)
    print(str)
    f.write(str+"\n")
    f.flush()
    lastRx[d.nodeid] = tNow
    #print d
    #print 
    #print dataset
    
    if test.ACKRequested():

        #test.sendACK()
        if test.RSSI > -60:
            txPowerChange = -6
        elif test.RSSI > -70:
            txPowerChange = -3
        elif test.RSSI < -80:
            txPowerChange = +3
        else:
            txPowerChange = 0

        txPowerChange = -80 - test.RSSI
        print("sendAck, txPowerChange: %d" % txPowerChange)
        data = struct.pack("Bb", 2, txPowerChange)
        test.sendACK(test.SENDERID, data);


print "shutting down"
test.shutdown()
