#!/usr/bin/env python3
'''
Move a motor back and forth using the TMCM1276 module
Created on 18.12.2019
@author: Amir Ahmady
for socket can please run this cmd in terminal:
# sudo ip link set can0 up type can bitrate 1000000
'''

import argparse
import csv
import time
from math import ceil

import PyTrinamic
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCM_1276 import TMCM_1276

from constant import *


def read_csv_file(filename="trajectory.csv", delimiter='\t', skip_header=False):
    with open(filename) as trajectory_file:
        reader = csv.reader(trajectory_file, delimiter=delimiter)
        if skip_header:
            next(reader)  # skip header
        data = [r for r in reader]
    return data


def selecting_column(data=list, column_number=0):
    return [float(i[column_number]) for i in data]


def shifting_data(data=list()):
    minimum_position = min(data)
    return [float(x) - minimum_position for x in data], minimum_position


def load_motion_data(filename, delimiter='\t'):
    data = read_csv_file(filename, delimiter=delimiter)
    x = selecting_column(data, 0)
    v = selecting_column(data, 1)
    a = selecting_column(data, 2)
    return x, v, a


def lead_per_pulse(stepping, leadScrewLead, unit='in'):
    if unit.lower() == 'in':
        lead = (leadScrewLead * 25.4) / (200 * stepping)  # 200 is stepper deg
    else:
        lead = 1
        pass
    return lead


def unit_to_pulse(mm, lead: float) -> int:
    try:
        return ceil(mm / lead)
    except ZeroDivisionError:
        raise(ZeroDivisionError)
        #lead = lead_per_pulse(256,)


def pulse_to_unit(pp, lead=lead):
    pp = -(MAX_RANGE-pp) if pp > 2147483647 else pp
    return round(pp*lead, 5)


def move_back_zoro(module_tmcm_1276, speed=153600):
    # print("current position is:", module_tmcm_1276.getActualPosition())
    # print("Moving back to 0")
    pos = 51200
    while pos > 20:
        pos = module_tmcm_1276.getActualPosition()
        move_to_pp(module_tmcm_1276, 0, speed)
        pos = -(MAX_RANGE-pos) if pos > 2147483647 else pos
    # print("Reached Position 0")


def move_by_unit(module_tmcm_1276, position: float, lead=lead, unit='SI') -> bool:
    """
    This function move stepper motor by desired Unit(SI "mm" or Imperial "inch")
    :param module_tmcm_1276:
    :param position:
    :param unit:
    :return:
    """
    _pos = unit_to_pulse(position, lead)
    # print()
    module_tmcm_1276.moveBy(_pos)
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


def move_to_pp(module_tmcm_1276, position: int, speed=MAX_SPEED) -> bool:
    """
    This function move stepper motor to desired Unit(pp)
    :param module_tmcm_1276:
    :param position:
    :param unit:
    :return:
    """
    # print(unit_to_pulse(position))
    module_tmcm_1276.moveTo(position, speed)
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
    parser.add_argument('-i', '--init', dest='init',
                        type=int, help='init movement')
    parser.add_argument('-r', '--RFS', dest='RFS_mode',
                        type=int, help="do refrence search")
    parser.add_argument('remaining_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    args.connection = output[args.connection]
    return args


def reference_search(module_tmcm_1276, mode=3, rfs_speed=200000, sw_telorance=0) -> bool:
    # TODO: set left and right position and define zero in regrading the mode
    # TODO: find right end
    # zero_telorance = int(unit_to_pulse(2))
    set_switch_Polarity(module_tmcm_1276, 0)
    zero_telorance = unit_to_pulse(sw_telorance, lead)
    soft_stop_toggle(module_tmcm_1276, False)
    end_sw_status = end_stop_sw_status(module_tmcm_1276)

    def right_end_position() -> int:
        rep = 0
        set_automatic_stop(module_tmcm_1276, False)
        module_tmcm_1276.rotate(rfs_speed)
        while module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.RightEndstop):
            print(module_tmcm_1276.getAxisParameter(
                module_tmcm_1276.APs.RightEndstop))
            pass
        module_tmcm_1276.stop()
        rep = module_tmcm_1276.getActualPosition()
        # set_automatic_stop(module_tmcm_1276,False)
        move_by_pp(module_tmcm_1276, -zero_telorance)
        return rep

    def left_end_position() -> int:
        lep = 0
        set_automatic_stop(module_tmcm_1276, False)
        module_tmcm_1276.rotate(-rfs_speed)
        while module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.LeftEndstop):
            pass
        module_tmcm_1276.stop()
        lep = module_tmcm_1276.getActualPosition()
        # set_automatic_stop(module_tmcm_1276,False)
        move_by_pp(module_tmcm_1276, zero_telorance)
        return lep

    def position_zero(rep=0, lep=0) -> int:
        print('Rep: ', rep, 'Lep: ', lep)
        lep = -(MAX_RANGE-lep) if lep > 2147483647 else lep
        rep = -(MAX_RANGE-rep) if rep > 2147483647 else rep
        if mode == 3:
            print('Rep: ', rep, 'Lep: ', lep)
            value = int((rep+lep)/2)
            dist = abs(lep-rep)-unit_to_pulse(2, lead)*2
            module_tmcm_1276.setAxisParameter(196, dist)
        else:
            print("This RFS's method is not implimented yet.")
            raise NotImplementedError
        return value

    # set_automatic_stop(module_tmcm_1276, all(end_stop_sw_status(module_tmcm_1276).values()))
    if all(end_sw_status.values()):  # all True
        print("Something is wrong in wiring")
        raise IOError
    elif not any(end_sw_status.values()):
        rep = right_end_position()
        # print(rep)
        lep = left_end_position()
        # print(lep)
        # TODO: find both side

    elif end_sw_status['R']:
        # TODO: find left side
        rep = module_tmcm_1276.getAxisParameter(
            module_tmcm_1276.APs.ActualPosition)
        lep = left_end_position()
        pass
    else:
        # TODO: find right side
        lep = module_tmcm_1276.getAxisParameter(
            module_tmcm_1276.APs.ActualPosition)
        rep = right_end_position()
        pass

    # set_position(module_tmcm_1276, position_zero(rep=rep,lep=lep))
    # print("ap is: ", module_tmcm_1276.getActualPosition())
    move_to_pp(module_tmcm_1276, position_zero(rep=rep, lep=lep), 51200)
    set_position(module_tmcm_1276, 0)
    print("RSF done, Moved to Zero")
    return True


def set_position(module_tmcm_1276, position=0):

    module_tmcm_1276.setActualPosition(position)
    while not (module_tmcm_1276.getActualPosition() == position):
        module_tmcm_1276.setActualPosition(position)
        pass
    print("Position set to: ", module_tmcm_1276.getActualPosition())

    # module_tmcm_1276.setAxisParameter(196,left_end_position)
    # print("ap 196 value:", module_tmcm_1276.getAxisParameter(196))

    # module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticRightStop, 0)
    # module_tmcm_1276.moveBy(100)
    # module_tmcm_1276.setActualPosition(0)
    # module_tmcm_1276.moveBy()


def test(module_tmcm_1276, mode=3, state=True):
    module_tmcm_1276.setAxisParameter(
        module_tmcm_1276.APs.ReferenceSearchMode, mode)
    module_tmcm_1276.setAxisParameter(194, 200000)
    module_tmcm_1276.setAxisParameter(196, 190000)
    print("ap 193 value:", module_tmcm_1276.getAxisParameter(193))

    #         return self.send(TMCL_Command.SAP, commandType, axis, value, moduleID)
    #     def move(self, moveType, motor, position, moduleID=None):
    #         return self.send(TMCL_Command.MVP, moveType, motor, position, moduleID)
    soft_stop_toggle(module_tmcm_1276, False)
    set_automatic_stop(module_tmcm_1276, True)
    print("RSF MODE")
    module_tmcm_1276.connection.send(13, 0, 0, 0)
    # RFS START, 0				//start reference search
    # WAIT RFS, 0, 1000			//wait until RFS is done or timeou
    print("wait")
    module_tmcm_1276.connection.send(27, 4, 0, 0)
    # module_tmcm_1276.connection.send(module_tmcm_1276.connection.TMCL_Command.MVP,0,0,1000,None)
    # module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.AutomaticRightStop, int(not state))
    # module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.ActualPosition)
    while not (module_tmcm_1276.positionReached()):
        pass


def set_automatic_stop(module_tmcm_1276, state: bool) -> bool:
    """
    :param module_tmcm_1276:
    :param state: bool False is on, True is off , in manual 1 is off 0 is on, maybe I should revers it for bool operator
    :return:
    """
    # module_tmcm_1276.setAxisParameter(module_tmcm_1276.APs.ReferenceSearchMode, 2)
    # TODO: It has know bug when set AP to 1 and it is not on stop switch start to find L switch. find a way to fix it.
    try:
        module_tmcm_1276.setAxisParameter(
            module_tmcm_1276.APs.AutomaticLeftStop, int(state))
        module_tmcm_1276.setAxisParameter(
            module_tmcm_1276.APs.AutomaticRightStop, int(state))
    except:
        print("some thing went wrong")
        return False
    else:
        right = module_tmcm_1276.getAxisParameter(
            module_tmcm_1276.APs.AutomaticRightStop)
        left = module_tmcm_1276.getAxisParameter(
            module_tmcm_1276.APs.AutomaticLeftStop)
        out = {'R': right, 'L':
               left}
        print("Auto Stop Mode", out)
        return state

    set_switch_Polarity(module_tmcm_1276, value=0)


def set_switch_Polarity(module_tmcm_1276, value=0):
    if module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.leftSwitchPolarity):
        module_tmcm_1276.setAxisParameter(
            module_tmcm_1276.APs.leftSwitchPolarity, value)
    if module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.rightSwitchPolarity):
        module_tmcm_1276.setAxisParameter(
            module_tmcm_1276.APs.rightSwitchPolarity, value)


def end_stop_sw_status(module_tmcm_1276) -> dict:

    right = module_tmcm_1276.getAxisParameter(
        module_tmcm_1276.APs.RightEndstop)
    right = not bool(right)
    left = module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.LeftEndstop)
    left = not bool(left)
    out = {'R': right, 'L': left}
    # print(out)
    return out


def soft_stop_toggle(module_tmcm_1276, toggle=True) -> bool:
    module_tmcm_1276.setAxisParameter(
        module_tmcm_1276.APs.softstop, int(toggle))
    return bool(module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.softstop))


def print_position(module_tmcm_1276, display=True):
    pos_pps = module_tmcm_1276.getActualPosition()
    pos_mm = pulse_to_unit(pos_pps, lead)
    print("PS: ", pos_pps, " mm :", pos_mm, 'lead:',lead)
    return(pos_pps, pos_mm)


def general_move(module_tmcm_1276, iteration=2):
    i = 0
    v = unit_to_pulse(20, lead)
    while i < iteration:
        module_tmcm_1276.rotate(v)
        time.sleep(1)
        module_tmcm_1276.stop()
        time.sleep(1)
        module_tmcm_1276.rotate(-v)
        time.sleep(1)
        module_tmcm_1276.stop()
        time.sleep(1)
        i += 1
    return print_position(module_tmcm_1276, display=False)


def run_trajectory(module_tmcm_1276, trajectory_data):
    start = time.time()
    for item in trajectory_data:
        start = time.time()
        print(item)
        move_to_unit(module_tmcm_1276, item*10)
        time_diff = time.time() - start
        if time_diff < 0.02:
            time.sleep(.02 - time_diff)


def motor_init(module_tmcm_1276, stepping=8, max_acceleration=300000, max_speed=300000):
    # print("MAX CUR",module_tmcm_1276.setAxisParameter(6,224))
    print("MAX CUR", module_tmcm_1276.getAxisParameter(6))
    print("Starting position is:", module_tmcm_1276.getActualPosition())
    module_tmcm_1276.setMaxAcceleration(max_acceleration)
    module_tmcm_1276.setMaxVelocity(max_speed)
    set_switch_Polarity(module_tmcm_1276, 0)
    module_tmcm_1276.setAxisParameter(
        module_tmcm_1276.APs.MicrostepResolution, stepping)
    module_tmcm_1276.setAxisParameter(21, 0)
    module_tmcm_1276.connection.printInfo()
    end_stop_sw_status(module_tmcm_1276)
    # test(module_tmcm_1276,2,True)
    soft_stop_toggle(module_tmcm_1276, False)
    print('max speed is:', module_tmcm_1276.getMaxVelocity())
    print("Current position is:", module_tmcm_1276.getActualPosition())
    names = ['Start velocity (V START ) ',
             'Acceleration A1 ',
             'Velocity V1',
             'Acceleration A2 ',
             'Maximum positioning velocity (V MAX )',
             'Deceleration D2',
             'Deceleration D1',
             'Stop velocity V STOP',
             'Wait time WAIT']
    aps = [19, 15, 16, 5, 4, 17, 18, 20, 21]
    for name, item in zip(names, aps):
        print(name, ': ', module_tmcm_1276.getAxisParameter(item))


def init_move_mm(module_tmcm_1276, lead=lead, move=None):
    init_move = move if move else int(input("desire init move by : "))
    print("pulse", unit_to_pulse(init_move, lead))
    set_automatic_stop(module_tmcm_1276, False)
    move_by_unit(module_tmcm_1276, init_move, lead=lead)
    print("Init move finished.")


def write_log(movement_log):
    for item in movement_log:
        item[2] = pulse_to_unit(item[2])
        item[3] = -(MAX_RANGE-item[3]) if item[3] > 2147483647 else item[3]
    with open('log_file.csv', mode='w') as log_file:
        log_writer = csv.writer(log_file, delimiter=',')
        log_writer.writerows(movement_log)


def velocity_movement(module_tmcm_1276, lead, maximum_velocity=10, filename="sin_taj.csv"):
    Hz = 1
    x, v, a = load_motion_data(filename, ',')
    max_v = max(v) if abs(max(v)) >= abs(min(v)) else abs(min(v))
    max_pps = unit_to_pulse(1, lead)
    if max_pps > 250000:
        print("Over speed")
        raise Exception
    c = max_pps  # / (max_v*Hz)
    v = v[::21]  # .02 values
    a = a[::21]  # .02 values
    v[:] = [ceil(c*item) for item in v]
    a[:] = [ceil(c*item) for item in a]
    i = 0
    movement_log = []
    while i < 1:
        module_tmcm_1276.stop()
        for item, a_item in zip(v[:-1], a[:-1]):
            module_tmcm_1276.rotate(item)
            module_tmcm_1276.setMaxAcceleration(a_item)
            time.sleep(.02)
        module_tmcm_1276.stop()
        i += 1
        print(i)
        print_position(module_tmcm_1276)
    module_tmcm_1276.setMaxAcceleration(MAX_SPEED)
    module_tmcm_1276.setMaxVelocity(MAX_SPEED)
    while module_tmcm_1276.getActualVelocity():
        module_tmcm_1276.stop()
    return movement_log


def main(*args):
    PyTrinamic.showInfo()
    connection_manager = ConnectionManager(
        argList=['--interface', args[0].connection])  # '--host-id',"4","--module-id","3"
    my_interface = connection_manager.connect()
    module_tmcm_1276 = TMCM_1276(my_interface)
    print("Warning if motor is not around postion zero it will go there automaticly")
    max_acceleration = int(MAX_SPEED*1.2)
    print(max_acceleration)
    default_motor = 0
    global lead
    lead = lead_per_pulse(256, 0.40, 'in')

    motor_init(module_tmcm_1276, STEPPING, max_acceleration, MAX_SPEED)

    end_stop_sw_status(module_tmcm_1276)

    if args[0].init:
        # module_tmcm_1276.rotate(350000)
        # time.sleep(4)
        # t=time.time()
        init_move_mm(module_tmcm_1276, args[0].init)
        temp = input("w8 for staring command")
        # print(module_tmcm_1276.getActualVelocity(),module_tmcm_1276.getMaxVelocity())
        # print(time.time()-t)

    if args[0].RFS_mode:
        reference_search(module_tmcm_1276, args[0].RFS_mode, sw_telorance=0)

    end_stop_sw_status(module_tmcm_1276)
    # **********************
    print("Current position is:", module_tmcm_1276.getActualPosition())
    end_stop_sw_status(module_tmcm_1276)
    set_automatic_stop(module_tmcm_1276, False)
    move_back_zoro(module_tmcm_1276)
    # module_tmcm_1276.rotate(-300000)
    temp = input("w8 for staring command")
    temp = input("w8 for staring command")
    # test(module_tmcm_1276,3)
    # module_tmcm_1276.setActualPosition(-unit_to_pulse(min_position))  # set start point of motor
    print_position(module_tmcm_1276)
    print("trajectory is loading")
    set_automatic_stop(module_tmcm_1276, False)
    # while True:
    #     end_stop_status(module_tmcm_1276)
    # movement_log = general_move(module_tmcm_1276)
    movement_log = velocity_movement(
        module_tmcm_1276, lead, 10, filename="sin_taj.csv")

    module_tmcm_1276.stop()
    time.sleep(.5)
    print_position(module_tmcm_1276)
    module_tmcm_1276.setMaxAcceleration(350000)
    move_back_zoro(module_tmcm_1276, 350000)
    print_position(module_tmcm_1276)
    write_log(movement_log)
    my_interface.close()


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
