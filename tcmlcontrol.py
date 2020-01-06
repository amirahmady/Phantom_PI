#!/usr/bin/env python3
'''
Move a motor back and forth using the TMCM1276 module
Created on 18.11.2019
@author: JM
'''

from __future__ import print_function
import PyTrinamic
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCM_1276 import TMCM_1276

import can
import canopen
import os
import time


bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)
# #msg = can.Message(arbitration_id=0x304,
#                   #data=[0, 1, 2, 3, 4, 5, 6, 7])
#
# try:
#     bus.send(msg)
#     print("Message sent on {}".format(bus.channel_info))
# except can.CanError:
#     print("Message NOT sent")

bus2= TMCM_1276.bus(bus)

PyTrinamic.showInfo()
print("USB Ports:")

connectionManager = ConnectionManager()
myInterface = connectionManager.connect()
TMCM_1276 = TMCM_1276(myInterface)

DEFAULT_MOTOR = 0

print("Preparing parameters")
TMCM_1276.setMaxAcceleration(9000)

print("Rotating")
TMCM_1276.rotate(40000)

time.sleep(5);

print("Stopping")
TMCM_1276.stop()

print("ActualPostion")
print(TMCM_1276.getActualPosition())
time.sleep(5);

print("Doubling moved distance")
TMCM_1276.moveBy(TMCM_1276.getActualPosition(), 50000)
TMCM_1276.getAxisParameter(TMCM_1276.APs.ActualPosition)
while not(TMCM_1276.positionReached()):
    pass

print("Furthest point reached")
print(TMCM_1276.getActualPosition())

time.sleep(5)

print("Moving back to 0")
TMCM_1276.moveTo(0, 100000)

# Wait until position 0 is reached
while not(TMCM_1276.positionReached()):
    pass

print("Reached Position 0")

print()

myInterface.close()