#!/usr/bin/env python3
'''
Move a motor back and forth using the TMCM1276 module
Created on 18.12.2019
@author: Amir Ahmady
for socket can please run this cmd in terminal:
$ sudo ip link set can0 up type can bitrate 1000000
'''

import argparse
import configparser
import csv
import json
import multiprocessing
import sys
import time
from math import ceil
from typing import Any, Callable, Iterable

import numpy as np
import PyTrinamic
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCM1276.TMCM_1276 import TMCM_1276

from constant import *
from generate_motion import calculate_motion
from sine_wave import Sine_Wave


class TMCM_1276A(TMCM_1276):
    def __init__(self, connection, adpt: float):
        super().__init__(connection)
        self.adpt = float(adpt)  # advance_per_turn
        try:
            self.axisId = super().getGlobalParameter(71, 0)
        except:
            pass
        self.lead = self.lead_per_pulse(256)

    def lead_per_pulse(self, stepping, unit='in'):
        """
            return in mm
        """
        if unit.lower() == 'in':
            lead = (1 * self.adpt * 25.4) / \
                (200 * stepping)  # 200 is stepper deg
        else:
            lead = 1
            pass
        self.lead = lead
        return lead

class Connection_Error(ConnectionError):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
        self._state = False

    def __str__(self):
        if self.message:
            return 'Connection_Error, {0} '.format(self.message)
        else:
            return 'Connection_Error has been raised'

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


def lead_per_pulse(stepping:int, advance_per_turn:float, unit='in'):
    if unit.lower() == 'in':
        # 25.4 is mm
        lead = (advance_per_turn * 25.4) / \
            (200 * stepping)  # 200 is stepper deg
    else:
        lead = 1
        pass
    return lead


def unit_to_pulse(mm:float, lead: float) -> int:
    try:
        return ceil(mm / lead)
    except ZeroDivisionError:
        print(lead)
        raise(ZeroDivisionError)
        # lead = lead_per_pulse(256,)


def pulse_to_unit(pp:int, lead:float):
    pp = -(MAX_RANGE-pp) if pp > 2147483647 else pp
    return round(pp*lead, 5)


def move_back_zero(module_tmcm_1276, speed=153600):
    # print("current position is:", module_tmcm_1276.getActualPosition())
    # print("Moving back to 0")
    pos = sys.maxsize
    while pos > 20:
        pos = module_tmcm_1276.getActualPosition()
        move_to_pp(module_tmcm_1276, 0, speed)
        pos = -(MAX_RANGE-pos) if pos > 2147483647 else pos
    # print("Reached Position 0")


def move_by_unit(module_tmcm_1276, position: float, lead:float, unit='SI') -> bool:
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
    moduleTMCM_1276.moveTo(unit_to_pulse(position, moduleTMCM_1276.lead))
    moduleTMCM_1276.getAxisParameter(moduleTMCM_1276.APs.ActualPosition)
    while not (moduleTMCM_1276.positionReached()):
        pass


def parse_arguments():

    def extra_axis(args):
        if args.extra_axises:
            s = args.extra_axises.split(",")
            try:
                s = list(map(float, s))
            except:
                print("All add axis arguments must be numbers.")
                raise(TypeError)
            finally:
                axis_out = [[] for i in range(int(s[0]))]
                n = 3
                try:
                    for item in range(int(s[0])):
                        axis_out[item].append(int(s[item*n+1]))
                        axis_out[item].append(int(s[item*n+2]))
                        axis_out[item].append(s[item*n+3])
                    args.extra_axises = axis_out
                except:
                    print("Invalid axis parameters.")
                    raise(AttributeError)

    parser = argparse.ArgumentParser(description='Respiration code')
    config = configparser.ConfigParser(
        allow_no_value=True, empty_lines_in_values=True, strict=True)
    config.read('config.ini')
    try:
        defaults = config['default']
    except KeyError:
        defaults = dict()
    defaults = dict(defaults)
    output = {"pcan": "pcan_tmcl",
              "p": "pcan_tmcl",
              "socketcan": "socketcan_tmcl",
              "s": "socketcan_tmcl",
              }
    if defaults.get("connection", False):
        parser.add_argument('-c', '--connection', dest='connection', choices=['socketcan', 'pcan'],
                            help="use socketcan or pcan as connection", required=False, type=str)
    else:
        parser.add_argument('-c', '--connection', dest='connection', choices=['socketcan', 'pcan'],
                            help="use socketcan or pcan as connection", required=True, type=str)
    parser.add_argument('-i', '--init', dest='init',
                        type=int, help='init movement')
    parser.add_argument('-r', '--RFS', dest='rfs_mode',
                        type=int, help="do refrence search")
    parser.add_argument('--host-id', dest='host_id', action='store', nargs=1, type=str, default='2',
                        help='TMCL host-id (default: %(default)s)')
    parser.add_argument('--module-id', dest='module_id', action='store', nargs=1, type=str, default='1',
                        help='TMCL module-id (default: %(default)s)')
    parser.add_argument('--adpt', dest='adpt', action='store', nargs=1, type=str, default='0.40',
                        help='Axis advance per turn(in). (default: %(default)s)')
    parser.add_argument('--add-axis', dest='extra_axises', action='store', type=str,
                        help='number of extra axises follow by module-id, host-id, advance per turn(in) "1,1,2,0.04"')
    parser.add_argument('otherthings', nargs="*")
    args = parser.parse_args()
    try:
        args.connection = output[args.connection]
    except:
        pass

    _args = vars(args)
    result = dict.fromkeys(_args)
    result.update(dict(defaults))
    # remove empty srtings from config file.
    result = {k: None if not v else v for k, v in result.items()}
    # Update if v is not None
    result.update({k: v for k, v in _args.items() if v is not None})
    result['init'] = int(
        result['init']) if result['init'] is not None else None
    result['rfs_mode'] = int(
        result['rfs_mode']) if result['rfs_mode'] is not None else None

    args = argparse.Namespace(**result)
    extra_axis(args)
    return args


def reference_search(module_tmcm_1276, mode=3, rfs_speed=200000, sw_telorance=0, axis=0) -> bool:
    # TODO: set left and right position and define zero in regrading the mode
    # TODO: find right end
    # zero_telorance = int(unit_to_pulse(2))
    lead=module_tmcm_1276.lead
    set_switch_Polarity(module_tmcm_1276, 0)
    zero_telorance = unit_to_pulse(sw_telorance, lead)
    soft_stop_toggle(module_tmcm_1276, False)
    end_sw_status = end_stop_sw_status(module_tmcm_1276)

    def right_end_position() -> int:
        rep = 0
        set_automatic_stop(module_tmcm_1276, False)
        module_tmcm_1276.rotate(rfs_speed)
        while module_tmcm_1276.getAxisParameter(module_tmcm_1276.APs.RightEndstop):
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

    def position_zero(rep=0, lep=0, axis=0) -> int:
        print('Rep: ', rep, 'Lep: ', lep)
        lep = -(MAX_RANGE-lep) if lep > 2147483647 else lep
        rep = -(MAX_RANGE-rep) if rep > 2147483647 else rep
        if mode == 3:
            # print('Rep: ', rep, 'Lep: ', lep,rep-lep)
            value = int((rep+lep)/2)
        else:
            print("This RFS's method is not implimented yet.")
            raise NotImplementedError

        file_name = 'ref_pos.json'

        with open(file_name) as json_file:
            data = json.load(json_file)
            dictionary = {
                "axis": axis,
                "lenght": value
            }
            data.update(dictionary)
            write_json(dictionary, file_name)
        return value

    # set_automatic_stop(module_tmcm_1276, all(end_stop_sw_status(module_tmcm_1276).values()))
    if all(end_sw_status.values()):  # all True
        print("Something is wrong in wiring")
        raise IOError
    elif not any(end_sw_status.values()):
        # find both side
        rep = right_end_position()
        # print(rep)
        lep = left_end_position()
        # print(lep)

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

    move_to_pp(module_tmcm_1276, position_zero(
        rep=rep, lep=lep, axis=axis), int(MAX_SPEED/4))
    set_position(module_tmcm_1276, 0)
    move_back_zero(module_tmcm_1276)
    print('ri:', module_tmcm_1276.getGlobalParameter(71, 0),"RSF has done, Moved to Zero")

    return True


def write_json(data, filename='data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def set_position(module_tmcm_1276, position=0):

    module_tmcm_1276.setActualPosition(position)
    while not (module_tmcm_1276.getActualPosition() == position):
        module_tmcm_1276.setActualPosition(position)
        pass
    print("Position set to: ", module_tmcm_1276.getActualPosition())




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
    """makh
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
    finally:
        right = module_tmcm_1276.getAxisParameter(
            module_tmcm_1276.APs.AutomaticRightStop)
        left = module_tmcm_1276.getAxisParameter(
            module_tmcm_1276.APs.AutomaticLeftStop)
        out = {'R': right, 'L':
               left}
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
    lead=module_tmcm_1276.lead
    pos_mm = pulse_to_unit(pos_pps, lead)
    print('RI:', module_tmcm_1276.getGlobalParameter(71, 0))
    print("     PS: ", pos_pps, " mm :", pos_mm, 'lead:', lead)
    return(pos_pps, pos_mm)


def general_move(module_tmcm_1276, iteration=2):
    i = 0
    try:
        v = unit_to_pulse(20, module_tmcm_1276.lead)
    except:
        v = 20000

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




def motor_init(module_tmcm_1276, stepping=8, max_acceleration=300000, max_speed=300000):
    # print("MAX CUR",module_tmcm_1276.setAxisParameter(6,224))
    print("MAX CUR", module_tmcm_1276.getAxisParameter(6))
    # Motor Will stop if no can msg for one second
    module_tmcm_1276.setGlobalParameter(82, 0, 1000)
    # Turn on cordinate storage to eeprom if set to 1
    module_tmcm_1276.setGlobalParameter(0, 84, 0)
    print("Starting position is:", module_tmcm_1276.getActualPosition())
    module_tmcm_1276.setMaxAcceleration(max_acceleration)
    module_tmcm_1276.setMaxVelocity(max_speed)
    set_switch_Polarity(module_tmcm_1276, 0)
    # MicroStep 8 =256
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


def init_move_mm(module_tmcm_1276, move=None, lead:float=0):
    init_move = move if move else int(input("desire init move by : "))
    lead = module_tmcm_1276.lead if lead == 0 else lead
    print("pulse", unit_to_pulse(init_move, lead))
    set_automatic_stop(module_tmcm_1276, False)
    move_by_unit(module_tmcm_1276, init_move, lead=lead)
    print("Init move finished.")


def write_log(movement_log,lead):
    for item in movement_log:
        item[2] = pulse_to_unit(item[2],lead)
        item[3] = -(MAX_RANGE-item[3]) if item[3] > 2147483647 else item[3]
    with open('log_file.csv', mode='w') as log_file:
        log_writer = csv.writer(log_file, delimiter=',')
        log_writer.writerows(movement_log)


def velocity_movement(module_tmcm_1276,data_source,enable_log=False,sample_rate=50,over_sample:int=None,loop_number=1):
    # TODO: Over X ?
    lead = module_tmcm_1276.lead
    def get_velocity_pram(v, a,step):
        # TODO: do calculatio regarding the Hz and sampling
        
        v = v if step==1 else v[::step]  # .02 values
        a = a if step==1 else a[::step]  # .02 values
        v[:] = [ceil(c*item) for item in v]
        a[:] = [ceil(c*item) for item in a]
        max_v =  abs(max(min(v), max(v), key=abs)) if type(v)== list else abs(max(v.min(), v.max(), key=abs))
        return max_v,v,a

    c = unit_to_pulse(1, lead)
    if type(data_source) == str:
        x, v, a = load_motion_data(data_source, ',')
    elif type(data_source) == tuple:
        x,v,a = data_source
    else:
        raise NotImplementedError



    max_v, v, a = get_velocity_pram(v, a,1) if over_sample is None else get_velocity_pram(v, a,over_sample)
    module_tmcm_1276.setMaxVelocity(MAX_SPEED)
    if max_v > MAX_SPEED:
        print("Over speed:", max_v)
        v[:] = [int(item) if item < MAX_SPEED else MAX_SPEED  for item in v]
        a[:] = [int(item) if item < MAX_SPEED else MAX_SPEED  for item in a]
    else :
        _v=list()
        _a=list()
        _v[:] = [int(item) for item in v]
        _a[:] = [int(item) for item in a]
        v=_v
        a=_a
        del _v,_a
   
    i = 0
    movement_log = []
    if enable_log:
        while i < loop_number:
            for v_item, a_item in zip(v, a):
                module_tmcm_1276.rotate(v_item)
                module_tmcm_1276.setMaxAcceleration(a_item)
                time.sleep(.02)
                movement_log.append([i,module_tmcm_1276.getActualPosition()])
            i += 1
    else:
        while i < loop_number:
            for v_item, a_item in zip(v, a):
                module_tmcm_1276.rotate(v_item)
                module_tmcm_1276.setMaxAcceleration(a_item)
                time.sleep(.02)
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
    max_acceleration = int(MAX_SPEED*1.2)

    axis_param = [[args[0].module_id, args[0].host_id, args[0].adpt]]
    axis_param = axis_param if args[0].extra_axises is None else axis_param + \
        args[0].extra_axises
    number_of_axis = len(axis_param)
    module_tmcm_1276 = list(range(number_of_axis))
    connection_manager = list(range(number_of_axis))
    my_interface = list(range(number_of_axis))


    C_Error = Connection_Error("")
    for idx, val in enumerate(axis_param):
        try:
            connection_manager[idx] = ConnectionManager(argList=['--interface', args[0].connection, '--module-id',
                                                                str(val[0]), '--host-id', str(val[1])])
            my_interface[idx] = connection_manager[idx].connect()
            module_tmcm_1276[idx] = (TMCM_1276A(my_interface[idx], val[2]))
            module_tmcm_1276[idx].stop()
        except ConnectionError as e:        
            
            err='\n{0} for module #{1}.\nPlease check connection and powerline on that Motor.\n'.format(
                e, module_tmcm_1276[idx].connection._MODULE_ID)
            print(err)
            C_Error.message=C_Error.message+err
            C_Error._state= True
    if  C_Error._state: raise C_Error



    print("Warning if motor is not around postion zero it will go there automatically")



    for tmcm in module_tmcm_1276:
        motor_init(tmcm, STEPPING, max_acceleration, MAX_SPEED)
        end_stop_sw_status(tmcm)

    if args[0].init:
        try:
            multi_process(module_tmcm_1276, init_move_mm, [int(args[0].init)])
            #init_move_mm(module_tmcm_1276[0], int(args[0].init))
        except TypeError:
            print("init Type Error")
        finally:
            temp = input("Waiting for starting command")

    if args[0].rfs_mode:
        multi_process(module_tmcm_1276, reference_search, [args[0].rfs_mode])
        print("RFS is done.")
    # **********************
    print("Current position is:", module_tmcm_1276[0].getActualPosition())
    for tmcm in module_tmcm_1276:
        end_stop_sw_status(tmcm)
        print_position(tmcm)
        set_automatic_stop(tmcm, False)

    multi_process(module_tmcm_1276,move_back_zero,[])


    # module_tmcm_1276.rotate(-300000)
    temp = input("Waiting for starting command")
    # test(module_tmcm_1276,3)
    # module_tmcm_1276.setActualPosition(-unit_to_pulse(min_position))  # set start point of motor
    for tmcm in module_tmcm_1276:
        print_position(tmcm)
        set_automatic_stop(tmcm, False)
    print("trajectory is loading")

    
    motion={x: [] for x in range(number_of_axis)}
    motion[0]=np.array(selecting_column(read_csv_file("complete.csv",'\t',False),0))
    motion[1]=np.array(selecting_column(read_csv_file("complete.csv",'\t',False),2))
    motion[0]=calc_motion(motion[0],"x-axis.csv")# *10 :converting cm to mm
    motion[1]=calc_motion(motion[1],"z-axis.csv")
   
    multi_process(module_tmcm_1276,velocity_movement,motion)
    #for idx, _motion in enumerate(motion):
    #    velocity_movement(module_tmcm_1276[idx],motion[idx])
    # while True:
    #     end_stop_status(module_tmcm_1276)
    # movement_log = general_move(module_tmcm_1276)

    #movement_log = velocity_movement(module_tmcm_1276[0], data_source="sin_taj.csv",over_data=True)

    for tmcm in module_tmcm_1276:
        tmcm.stop()

    time.sleep(.5)

    for tmcm in module_tmcm_1276:
        print_position(tmcm)
        tmcm.setMaxAcceleration(MAX_SPEED)
    multi_process(module_tmcm_1276, move_back_zero, [MAX_SPEED])
    for tmcm in module_tmcm_1276:
        print_position(tmcm)

    # write_log(movement_log)

    for interface in my_interface:
        interface.close()

def calc_motion(x,output_file:str=None):
    v ,a =  calculate_motion(x)
    if output_file is not None:
        with open('output_file', mode='w') as log_file:
            log_writer = csv.writer(log_file, delimiter=',')
            log_writer.writerow(["x","v","a"])
            log_writer.writerows([x, v ,a])
    return x,v,a

def multi_process(module_tmcm_1276, func_name: Callable[..., Any], func_args: Iterable[Any] =list()):
    cmd = []
    #if len(func_args) <> len(module_tmcm_1276)
    _func_args = [[] for x in range(len(module_tmcm_1276))]
    if type(func_args)==list:

        for idx,tmcm in enumerate(module_tmcm_1276):
            _func_args[idx]=[tmcm]+func_args
    elif type(func_args)==dict:
        for tmcm, idx in zip(module_tmcm_1276,func_args):
            _func_args[idx].append(tmcm)
            _func_args[idx].append(func_args[idx])
    else:
        raise NotImplementedError
    for idx, tmcm in enumerate(module_tmcm_1276):
        cmd.append(multiprocessing.Process(target=func_name,
                                           args=_func_args[idx]))
    for item in cmd:
        item.start()
    for item in cmd:
        item.join()


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
