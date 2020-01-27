#!/usr/bin/env python3
'''
Move a motor back and forth using the TMCM1276 module
Created on 18.12.2019
@author: Amir Ahmady
'''
# sudo ip link set can0 up type can bitrate 1000000


import argparse
import csv
import time

import PyTrinamic
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCM_1276 import TMCM_1276


def read_csv_file(filename="trajectory.csv"):
    with open("trajectory.csv") as trajectory_file:
        reader = csv.reader(trajectory_file, delimiter='\t')
        next(reader)  # skip header
        data = [r for r in reader]
    return data


def selecting_column(data=list, column_number=0):
    return [float(i[column_number]) for i in data]


def shifting_data(data=list()):
    minimum_position = min(data)
    return [float(x) - minimum_position for x in data], minimum_position


def lead_per_pulse(stepping, leadScrewLead, unit='in'):
    if unit.lower() == 'in':
        lead = (leadScrewLead * 25.4) / (200 * stepping)  # 200 is stepper deg
    else:
        lead = 1
        pass
    return lead


def unit_to_pulse(mm, lead=4.9609375e-05):
    return round(mm / lead)


def move_back_zoro(moudule_tmcm_1276, speed=150000):
    print("current position is:", moudule_tmcm_1276.getActualPosition())
    print("Moving back to 0")
    moudule_tmcm_1276.moveTo(0, speed)
    # Wait until position 0 is reached
    while not (moudule_tmcm_1276.positionReached()):
        pass
    print("Reached Position 0")


def move_by_unit(moudule_tmcm_1276, position: float, unit='SI') -> bool:
    """
    This function move stepper motor by desired Unit(SI "mm" or Imperial "inch")
    :param moudule_tmcm_1276:
    :param position:
    :param unit:
    :return:
    """
    #print(unit_to_pulse(position))
    moudule_tmcm_1276.moveBy(unit_to_pulse(position))
    moudule_tmcm_1276.getAxisParameter(moudule_tmcm_1276.APs.ActualPosition)
    while not (moudule_tmcm_1276.positionReached()):
        pass


def move_to_unit(mouduleTMCM_1276, position, unit='SI'):
    # add in or si postioning
    # print(position, move_by_mm(position))
    mouduleTMCM_1276.moveTo(unit_to_pulse(position))
    mouduleTMCM_1276.getAxisParameter(mouduleTMCM_1276.APs.ActualPosition)
    while not (mouduleTMCM_1276.positionReached()):
        pass


def parse_arguments():
    parser = argparse.ArgumentParser(description='Respiration code')
    output = {"pcan": "pcan_tmcl",
              "p": "pcan_tmcl",
              "socketcan": "socketcan_tmcl",
              "s": "socketcan_tmcl"
              }
    parser.add_argument('-c', '--connection', dest='connection', choices=['socketcan', 'pcan'],
                        help="use socketcan or pcan as connection", required=True, type=str)
    parser.add_argument('remaining_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    return output[args.connection]


def reference_search(moudule_tmcm_1276, mode=2):
    # TODO: set left and right position and define zero in regrading the mode
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.ReferenceSearchMode, mode)
    # moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.Ref)
    automatic_stop_toggle(moudule_tmcm_1276, 1)
    # TODO: find left end
    end_stop_status(moudule_tmcm_1276)
    #while moudule_tmcm_1276.getAxisParameter(moudule_tmcm_1276.APs.LeftEndstop):
    #    moudule_tmcm_1276.moveBy(51700)

    # TODO: find right end
    end_stop_status(moudule_tmcm_1276)
    while moudule_tmcm_1276.getAxisParameter(moudule_tmcm_1276.APs.RightEndstop):
        #end_stop_status(moudule_tmcm_1276)
        moudule_tmcm_1276.moveBy(-51700)
    moudule_tmcm_1276.stop()
    moudule_tmcm_1276.setActualPosition(0)
    while not (moudule_tmcm_1276.getActualPosition()==0):
        print(moudule_tmcm_1276.getActualPosition())
        moudule_tmcm_1276.setActualPosition(0)
        pass
    #moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.AutomaticRightStop, 0)
    #moudule_tmcm_1276.moveBy(100)
    #moudule_tmcm_1276.setActualPosition(0)
        # moudule_tmcm_1276.moveBy()


def automatic_stop_toggle(moudule_tmcm_1276, state):
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.AutomaticRightStop, state)
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.AutomaticLeftStop, state)


def end_stop_status(moudule_tmcm_1276):
    print("R:", moudule_tmcm_1276.getAxisParameter(moudule_tmcm_1276.APs.RightEndstop), "L:",
          moudule_tmcm_1276.getAxisParameter(moudule_tmcm_1276.APs.LeftEndstop))


def soft_stop_toggle(moudule_tmcm_1276, toggle=True) -> bool:
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.softstop, int(toggle))
    return moudule_tmcm_1276.getAxisParameter(moudule_tmcm_1276.APs.softstop)


def main(*args):
    PyTrinamic.showInfo()
    print(args[0])
    connection_manager = ConnectionManager(argList=['--interface', args[0]])

    # myInterface = "pcan_tmcl"
    my_interface = connection_manager.connect()
    moudule_tmcm_1276 = TMCM_1276(my_interface)
    max_speed = 12800 * 3
    max_acceleration = max_speed * 2
    default_motor = 0
    stepping = 256
    lead = lead_per_pulse(256, 0.10, 'in')

    moudule_tmcm_1276.setMaxAcceleration(max_acceleration)
    moudule_tmcm_1276.setMaxVelocity(max_speed)
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.CurrentStepping, stepping)
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.AutomaticRightStop, 1)
    moudule_tmcm_1276.setAxisParameter(moudule_tmcm_1276.APs.AutomaticLeftStop, 1)
    print('max speed is:', moudule_tmcm_1276.getMaxVelocity())
    print("Start position is:", moudule_tmcm_1276.getActualPosition())
    move_by_unit(moudule_tmcm_1276, 10)

    # moudule_tmcm_1276.setActualPosition(0)
    # *********************
    print(moudule_tmcm_1276.connection.printInfo())
    print(soft_stop_toggle(moudule_tmcm_1276))
    reference_search(moudule_tmcm_1276, 2)
    end_stop_status(moudule_tmcm_1276)
    print("current position is:", moudule_tmcm_1276.getActualPosition())

    temp = input("w8")
    print(temp)
    # **********************
    print("current position is:", moudule_tmcm_1276.getActualPosition())
    end_stop_status(moudule_tmcm_1276)
    print("current position is:", moudule_tmcm_1276.getAxisParameter(196))
    move_back_zoro(moudule_tmcm_1276)
    temp = input("w8")


    print(temp)
    trajectory_file = "trajectory.csv"
    trajectory_data, min_position = shifting_data(selecting_column(read_csv_file(trajectory_file), column_number=0))

    start = time.time()
    moudule_tmcm_1276.setActualPosition(-unit_to_pulse(min_position))  # set start point of motor
    print("trajectory is loading")
    for item in trajectory_data:
        start = time.time()
        move_to_unit(moudule_tmcm_1276, item)
        time_diff = time.time() - start
        if time_diff < 0.02:
            time.sleep(.02 - time_diff)

    move_back_zoro(moudule_tmcm_1276)
    my_interface.close()


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
