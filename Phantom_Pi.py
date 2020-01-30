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

step_range = 2147483647 * 2


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


def move_back_zoro(module_tmcm_1276, speed=75000):
    print("current position is:", module_tmcm_1276.getActualPosition())
    print("Moving back to 0")
    module_tmcm_1276.moveTo(0, speed)
    # Wait until position 0 is reached
    while not (module_tmcm_1276.positionReached()):
        pass
    print("Reached Position 0")


def move_by_unit(module_tmcm_1276, position: float, unit='SI') -> bool:
    """
    This function move stepper motor by desired Unit(SI "mm" or Imperial "inch")
    :param module_tmcm_1276:
    :param position:
    :param unit:
    :return:
    """
    # print(unit_to_pulse(position))
    module_tmcm_1276.moveBy(unit_to_pulse(position))
    module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.ActualPosition)
    while not (module_tmcm_1276.positionReached()):
        pass

def move_by_pp(module_tmcm_1276, position: int) -> bool:
    """
    This function move stepper motor by desired Unit(pp)
    :param module_tmcm_1276:
    :param position:
    :param unit:
    :return:
    """
    # print(unit_to_pulse(position))
    module_tmcm_1276.moveBy(position)
    module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.ActualPosition)
    while not (module_tmcm_1276.positionReached()):
        pass
    return True

def move_to_unit(moduleTMCM_1276, position, unit='SI'):
    # add in or si postioning
    # print(position, move_by_mm(position))
    moduleTMCM_1276.moveTo(unit_to_pulse(position))
    moduleTMCM_1276.getAxisParameter(moduleTMCM_1276.APs.ActualPosition)
    while not (moduleTMCM_1276.positionReached()):
        pass


def parse_arguments():
    parser = argparse.ArgumentParser(description='Respiration code')
    output = {"pcan": "pcan_tmcl",
              "p": "pcan_tmcl",
              "socketcan": "socketcan_tmcl",
              "s": "socketcan_tmcl",
              }
    parser.add_argument('-c', '--connection', dest='connection', choices=['socketcan', 'pcan'],
                        help="use socketcan or pcan as connection", required=True, type=str)
    parser.add_argument('-i','--init',dest='init',type=int,help='init movement')                    
    parser.add_argument('remaining_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    args.connection = output[args.connection]
    return args


def reference_search(module_tmcm_1276, mode=3):
    print("Doing reference search by mode {0} ...".format(mode))
    print(module_tmcm_1276.getAxisParameter(196),module_tmcm_1276.getAxisParameter(197))
    zero_telorance= int(unit_to_pulse(-5))

    # TODO: set left and right position and define zero in regrading the mode
    # TODO: find right end
    
    end_stop_status(module_tmcm_1276)
    automatic_stop_toggle(module_tmcm_1276, True)
    while module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.RightEndstop):
        module_tmcm_1276.moveBy(-51700)
    module_tmcm_1276.stop()
    right_end_position = module_tmcm_1276.getActualPosition()
    virtual_zero = step_range + zero_telorance if right_end_position > 2147483647 else step_range - zero_telorance #right point what if it is small positive?
    print('0: ', virtual_zero)
    set_positon(module_tmcm_1276, virtual_zero)
    automatic_stop_toggle(module_tmcm_1276, False)
    move_back_zoro(module_tmcm_1276)
    print("right switch found:", right_end_position)
    print("right end set as:", module_tmcm_1276.getActualPosition())

    # TODO: find left end

    end_stop_status(module_tmcm_1276)
    automatic_stop_toggle(module_tmcm_1276, True)
    while module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.LeftEndstop):
        module_tmcm_1276.moveBy(51700)
    module_tmcm_1276.stop()
    while not (module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.ActualVelocity) == 0):
        pass
    left_end_position = module_tmcm_1276.getActualPosition()+ zero_telorance 
    automatic_stop_toggle(module_tmcm_1276, False)
    move_by_pp(module_tmcm_1276,zero_telorance)
    print("left switch found:", left_end_position)
    if mode == 3 :
        position_zero = int(left_end_position/2)
    else:
        position_zero = right_end_position
    set_positon(module_tmcm_1276, position_zero)
    print("ap is: ", module_tmcm_1276.getActualPosition())
    move_back_zoro(module_tmcm_1276)


def set_positon(module_tmcm_1276, position:int):

    module_tmcm_1276.setActualPosition(position)
    while not (module_tmcm_1276.getActualPosition() == position):
        # print(module_tmcm_1276.getActualPosition())
        module_tmcm_1276.setActualPosition(position)
        pass
    print("Position set to: ", module_tmcm_1276.getActualPosition())

    #module_tmcm_1276.setAxisParameter(196,left_end_position)
    #print("ap 196 value:", module_tmcm_1276.getAxisParameter(196))

    # module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticRightStop, 0)
    # module_tmcm_1276.moveBy(100)
    # module_tmcm_1276.setActualPosition(0)
    # module_tmcm_1276.moveBy()

def test(module_tmcm_1276, mode=2, state = True):
    module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.ReferenceSearchMode, mode)
    print("ap 193 value:", module_tmcm_1276.getAxisParameter(193))
    #         return self.send(TMCL_Command.SAP, commandType, axis, value, moduleID)
    #     def move(self, moveType, motor, position, moduleID=None):
    #         return self.send(TMCL_Command.MVP, moveType, motor, position, moduleID)
    soft_stop_toggle(module_tmcm_1276, False)
    automatic_stop_toggle(module_tmcm_1276,True)
    print("RSF MODE")
    module_tmcm_1276.connection.send(13, 0, 0, 0)
    #RFS START, 0				//start reference search
    #WAIT RFS, 0, 1000			//wait until RFS is done or timeou
    print("wait")
    module_tmcm_1276.connection.send(27, 4, 0, 10000)
    #module_tmcm_1276.connection.send(module_tmcm_1276.connection.TMCL_Command.MVP,0,0,1000,None)
    #module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticRightStop, int(not state))
    #module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.ActualPosition)
    while not (module_tmcm_1276.positionReached()):
        pass
    right_end_position = module_tmcm_1276.getActualPosition()
    print("right switch found:", right_end_position)
    #print("right end set as starting piont", module_tmcm_1276.getActualPosition())
    print("ap 196 value:", module_tmcm_1276.getAxisParameter(196))

    module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticRightStop, int(state))
    module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticLeftStop, int(not state))
    module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.ActualPosition)
    while not (module_tmcm_1276.positionReached()):
        pass
    left_end_position = module_tmcm_1276.getActualPosition()
    print("left switch found:", left_end_position)
    print("ap 196 value:", module_tmcm_1276.getAxisParameter(196))
    return True

def automatic_stop_toggle(module_tmcm_1276, state: bool) -> bool:
    """
    :param module_tmcm_1276:
    :param state: bool True is on, False is off
    :return:
    """
    #module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.ReferenceSearchMode, 2)
    # TODO: It has know bug when set AP to 1 and it is not on stop switch start to find L switch. find a way to fix it.
    print(module_tmcm_1276.getAxisParameter(193))
    try:
        module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticLeftStop, int(not state))
        module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticRightStop, int(not state))
    except:
        return False
    else:
        return True


def end_stop_status(module_tmcm_1276):
    print("R:", module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.RightEndstop), "L:",
          module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.LeftEndstop))


def soft_stop_toggle(module_tmcm_1276, toggle=True) -> bool:
    module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.softstop, int(toggle))
    return bool(module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.softstop))


def main(*args):
    PyTrinamic.showInfo()
    connection_manager = ConnectionManager(argList=['--interface', args[0].connection])
    my_interface = connection_manager.connect()
    module_tmcm_1276 = TMCM_1276(my_interface)

    max_speed = 12800 * 3 * 2
    max_acceleration = max_speed * 2
    default_motor = 0
    stepping = 256
    lead = lead_per_pulse(256, 0.10, 'in')

    motor_init(max_acceleration, max_speed, module_tmcm_1276, stepping)
    #automatic_stop_toggle(module_tmcm_1276, ‌)

    #init_move_mm(module_tmcm_1276)
    #test(module_tmcm_1276, mode=1, state=True)


    


    if args[0].init : init_move_mm(module_tmcm_1276,args[0].init)

    # module_tmcm_1276.setActualPosition(0)
    # *********************
    reference_search(module_tmcm_1276, 2)
    end_stop_status(module_tmcm_1276)
    print("Current position is:", module_tmcm_1276.getActualPosition())

    temp = input("w8")
    print(temp)
    # **********************
    print("Current position is:", module_tmcm_1276.getActualPosition())
    end_stop_status(module_tmcm_1276)
    print("current position is:", module_tmcm_1276.getAxisParameter(196))
    move_back_zoro(module_tmcm_1276)
    temp = input("w8")

    print(temp)
    trajectory_file = "trajectory.csv"
    trajectory_data, min_position = shifting_data(selecting_column(read_csv_file(trajectory_file), column_number=0))

    start = time.time()
    module_tmcm_1276.setActualPosition(-unit_to_pulse(min_position))  # set start point of motor
    print("trajectory is loading")
    for item in trajectory_data:
        start = time.time()
        move_to_unit(module_tmcm_1276, item)
        time_diff = time.time() - start
        if time_diff < 0.02:
            time.sleep(.02 - time_diff)

    move_back_zoro(module_tmcm_1276)
    my_interface.close()


def motor_init(max_acceleration, max_speed, module_tmcm_1276, stepping):
    print("Starting position is:", module_tmcm_1276.getActualPosition())
    module_tmcm_1276.setMaxAcceleration(max_acceleration)
    module_tmcm_1276.setMaxVelocity(max_speed)
    module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.CurrentStepping, stepping)
    module_tmcm_1276.connection.printInfo()
    end_stop_status(module_tmcm_1276)
    #test(module_tmcm_1276,2,True)
    soft_stop_toggle(module_tmcm_1276)
    print('max speed is:', module_tmcm_1276.getMaxVelocity())
    print("Current position is:", module_tmcm_1276.getActualPosition())


def init_move_mm(module_tmcm_1276,move=None):
    init_move = move if move else int(input("desire init move by : "))
    print("pulse",unit_to_pulse(init_move))
    automatic_stop_toggle(module_tmcm_1276, False)
    move_by_unit(module_tmcm_1276, init_move)
    print("done")

#def set_zero_position(0)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
