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
import csv


def read_csv_file(filename="trajectory.csv"):
    with open("trajectory.csv") as trajFile:
        reader = csv.reader(trajFile, delimiter='\t')
        next(reader)  # skip header
        data = [r for r in reader]
    return data




def main():
    PyTrinamic.showInfo()
    print("PyTrinamic.showInfo()")
    connectionManager = ConnectionManager(argList=['--interface', 'pcan_tmcl'])
    # myInterface = "pcan_tmcl"
    myInterface = connectionManager.connect()
    mouduleTMCM_1276 = TMCM_1276(myInterface)
    maxSpeed = 12800
    DEFAULT_MOTOR = 0
    Stepping = 256
    i = 0
    CANBitrate = 200
    print("Preparing parameters")

    mouduleTMCM_1276.setMaxAcceleration(100000)
    mouduleTMCM_1276.setMaxVelocity(maxSpeed)
    mouduleTMCM_1276.setAxisParameter(mouduleTMCM_1276.APs.CurrentStepping, Stepping)
    print("Start position is:", mouduleTMCM_1276.getActualPosition())
    # print(TMCM_1276.getGlobalParameter(CANBitrate,bank),CANBitrate,'***',bank)
    mouduleTMCM_1276.moveBy(mouduleTMCM_1276.getActualPosition()+10000)
    mouduleTMCM_1276.getAxisParameter(mouduleTMCM_1276.APs.ActualPosition)
    while not (mouduleTMCM_1276.positionReached()):
        pass

    trajectoryFile = "trajectory.csv"
    trajectoryData = read_csv_file(trajectoryFile)
    start = time.time()
    i=0
    for item in trajectoryData[:100]:
        i = i+1
        print(i, item[0])
        print(round(float(item[0])*10))
        # TMCM_1276.moveBy(TMCM_1276.getActualPosition() + round(float(item[0])*10))
        # TMCM_1276.getAxisParameter(TMCM_1276.APs.ActualPosition)
        # while not (TMCM_1276.positionReached()):
        #     pass
    end = time.time()
    print(end - start)
    # TMCM_1276.setAxisParameter(TMCM_1276.APs.CurrentStepping, 0)
    print("Moving back to 0")
    #TMCM_1276.moveTo(0, 100000)

    # Wait until position 0 is reached
    #while not (TMCM_1276.positionReached()):
        #pass

    #myInterface.close()

if __name__== "__main__":
  main()
