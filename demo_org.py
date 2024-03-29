#!/usr/bin/env python3
'''
Move a motor back and forth using the TMCM1276 module
Created on 18.11.2019
@author: JM
'''

import PyTrinamic
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCM_1276 import TMCM_1276
import time

PyTrinamic.showInfo()
connectionManager = ConnectionManager(
        argList=['--interface', 'pcan_tmcl', '--module-id',"1",'--host-id','2'])
#connectionManager = ConnectionManager()
myInterface = connectionManager.connect()
TMCM_1276 = TMCM_1276(myInterface)
print('si',TMCM_1276.getGlobalParameter(70,0))
print('ri',TMCM_1276.getGlobalParameter(71,0))
#TMCM_1276.setGlobalParameter(70,0,1)
DEFAULT_MOTOR = 0

print("Preparing parameters")
TMCM_1276.setMaxAcceleration(9000)

print("Stopping")
TMCM_1276.stop()
temp=input("press return")
print("Rotating")
TMCM_1276.rotate(20000)

time.sleep(5)

print("Stopping")
TMCM_1276.stop()

print("ActualPostion") 
print(TMCM_1276.getActualPosition())
time.sleep(5);

print("Doubling moved distance")
TMCM_1276.moveBy(TMCM_1276.getActualPosition(), 20000)
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