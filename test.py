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


def lead_per_pulse(stepping, leadScrewLead, leadScrewDimension='in'):
    if leadScrewDimension.lower() == 'in':
        lead = (leadScrewLead*25.4)/(200*stepping) # 200 is stepper deg
    else:
        lead = 1
        pass
    return lead


def move_by_mm(mm, lead = 4.9609375e-05):
    return round(mm/lead)



def move_back_zoro(mouduleTMCM_1276, speed = 150000):
    print("Moving back to 0")
    mouduleTMCM_1276.moveTo(0, speed)
    # Wait until position 0 is reached
    while not (mouduleTMCM_1276.positionReached()):
        pass

    print("Reached Position 0")


def main():
    PyTrinamic.showInfo()
    print("PyTrinamic.showInfo()")
    connectionManager = ConnectionManager(argList=['--interface', 'pcan_tmcl'])
    # myInterface = "pcan_tmcl"
    myInterface = connectionManager.connect()
    mouduleTMCM_1276 = TMCM_1276(myInterface)
    maxSpeed = 12800
    maxAcceleration = 100000
    DEFAULT_MOTOR = 0
    Stepping = 256
    i = 0
    CANBitrate = 200
    print("Preparing parameters")
    lead = lead_per_pulse(256,0.10,'in')
    print(lead)
    mouduleTMCM_1276.setMaxAcceleration(maxAcceleration)
    mouduleTMCM_1276.setMaxVelocity(maxSpeed)
    mouduleTMCM_1276.setAxisParameter(mouduleTMCM_1276.APs.CurrentStepping, Stepping)
    print("Start position is:", mouduleTMCM_1276.getActualPosition())
    # print(TMCM_1276.getGlobalParameter(CANBitrate,bank),CANBitrate,'***',bank)
    moveBymm = move_by_mm(2.54)
    print(moveBymm)
    mouduleTMCM_1276.moveBy(moveBymm)
    mouduleTMCM_1276.getAxisParameter(mouduleTMCM_1276.APs.ActualPosition)
    while not (mouduleTMCM_1276.positionReached()):
        pass

    # trajectoryFile = "trajectory.csv"
    # trajectoryData = read_csv_file(trajectoryFile)
    # start = time.time()
    # i=0
    # for item in trajectoryData[:100]:
    #     i = i+1
    #     print(i, item[0])
    #     print(round(float(item[0])*10))
    #     # TMCM_1276.moveBy(TMCM_1276.getActualPosition() + round(float(item[0])*10))
    #     # TMCM_1276.getAxisParameter(TMCM_1276.APs.ActualPosition)
    #     # while not (TMCM_1276.positionReached()):
    #     #     pass
    # end = time.time()
    # print(end - start)
    # # TMCM_1276.setAxisParameter(TMCM_1276.APs.CurrentStepping, 0)
    # print("Moving back to 0")
    # #TMCM_1276.moveTo(0, 100000)
    #
    # # Wait until position 0 is reached
    # #while not (TMCM_1276.positionReached()):
    #     #pass
    move_back_zoro(mouduleTMCM_1276)
    myInterface.close()

if __name__== "__main__":
  main()
