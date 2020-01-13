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

def selecting_first_col(data=list):


def shifting_data(data=list()):
    minimum_postition = min(data)
    for item in data:
        item = item
def lead_per_pulse(stepping, leadScrewLead, unit='in'):
    if unit.lower() == 'in':
        lead = (leadScrewLead * 25.4) / (200 * stepping)  # 200 is stepper deg
    else:
        lead = 1
        pass
    return lead


def move_by_mm(mm, lead=4.9609375e-05):
    return round(mm / lead)


def move_back_zoro(mouduleTMCM_1276, speed=150000):
    print("Moving back to 0")
    mouduleTMCM_1276.moveTo(0, speed)
    # Wait until position 0 is reached
    while not (mouduleTMCM_1276.positionReached()):
        pass

    print("Reached Position 0")

def move_to_pos(mouduleTMCM_1276, position, unit='SI'):
    # add in or si postioning
    mouduleTMCM_1276.moveBy(move_by_mm(position))
    mouduleTMCM_1276.getAxisParameter(mouduleTMCM_1276.APs.ActualPosition)
    while not (mouduleTMCM_1276.positionReached()):
        pass


def main():
    PyTrinamic.showInfo()
    print("Preparing parameters")
    connectionManager = ConnectionManager(argList=['--interface', 'pcan_tmcl'])
    # myInterface = "pcan_tmcl"
    myInterface = connectionManager.connect()
    mouduleTMCM_1276 = TMCM_1276(myInterface)
    maxSpeed = 12800
    maxAcceleration = 50000
    DEFAULT_MOTOR = 0
    Stepping = 256
    lead = lead_per_pulse(256, 0.10, 'in')

    mouduleTMCM_1276.setMaxAcceleration(maxAcceleration)
    mouduleTMCM_1276.setMaxVelocity(maxSpeed)
    mouduleTMCM_1276.setAxisParameter(mouduleTMCM_1276.APs.CurrentStepping, Stepping)
    print('max speed is:', mouduleTMCM_1276.getMaxVelocity())
    print("Start position is:", mouduleTMCM_1276.getActualPosition())
    move_back_zoro(mouduleTMCM_1276)

    # moveBymm = move_by_mm(0.1)
    # print(moveBymm)
    # mouduleTMCM_1276.moveBy(moveBymm)
    # mouduleTMCM_1276.getAxisParameter(mouduleTMCM_1276.APs.ActualPosition)
    # while not (mouduleTMCM_1276.positionReached()):
    #     pass
    # print("The position is:", mouduleTMCM_1276.getActualPosition())

    trajectoryFile = "trajectory.csv"
    trajectoryData = read_csv_file(trajectoryFile)
    start = time.time()
    curentPostion = 0
    for item in trajectoryData[400:600]:
        moveTo = float(item[0]) - curentPostion
        move_to_pos(mouduleTMCM_1276, moveTo)
        curentPostion = moveTo
    end = time.time()
    print(end - start)

    move_back_zoro(mouduleTMCM_1276)
    myInterface.close()


if __name__ == "__main__":
    main()
