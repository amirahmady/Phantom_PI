#!/usr/bin/env python3
'''
Move a motor back and forth using the TMCM1276 module
Created on 18.11.2019
@author: JM
'''

import multiprocessing
import time
import math

import PyTrinamic
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCM_1276 import TMCM_1276
from Phantom_Pi import end_stop_sw_status
from Phantom_Pi import set_automatic_stop

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])


def movment(TMCM, speed, duriation):
    TMCM.rotate(speed)
    time.sleep(duriation)
    TMCM.stop()
    for tmcm in module_tmcm_1276:
        set_automatic_stop(tmcm, False)
    print('ri:', TMCM.getGlobalParameter(71, 0),
        'stoped @:', time.localtime().tm_sec, 'sec')


my_interface = [None, None]
module_tmcm_1276 = [None, None]
connection_manager = [None, None]

PyTrinamic.showInfo()
connection_manager[0] = ConnectionManager(
    argList=['--interface', 'socketcan_tmcl', '--module-id', "1", '--host-id', '2'])
my_interface[0] = connection_manager[0].connect()
module_tmcm_1276[0] = TMCM_1276(my_interface[0])

connection_manager[1] = ConnectionManager(
    argList=['--interface', 'socketcan_tmcl', '--module-id', "4", '--host-id', '5'])
my_interface[1] = connection_manager[1].connect()
module_tmcm_1276[1] = TMCM_1276(my_interface[1])

module_tmcm_1276[1].stop()
module_tmcm_1276[0].stop()


print("Preparing parameters")
for idx, tmcm in enumerate(module_tmcm_1276):
    tmcm.setMaxAcceleration(100000)
    tmcm.setMaxVelocity(150000)
    del tmcm

for idx, tmcm in enumerate(module_tmcm_1276):
    print("{0} Motor:".format(ordinal(idx+1)))
    print('si', tmcm.getGlobalParameter(70, 0))
    print('ri', tmcm.getGlobalParameter(71, 0))
    del tmcm


print("Stopping")
for tmcm in module_tmcm_1276:
    tmcm.stop()
    del tmcm

""" while True:
    for tmcm in module_tmcm_1276:
       end_sw_status=  end_stop_sw_status(tmcm)
       print(tmcm.getGlobalParameter(71, 0),": ",end_sw_status)
    if any(end_sw_status.values()):
        time.sleep(.5) """


temp = input("Enter for test movment, any other input for End: ")
if temp.lower() == 'end' or not temp=='':
    print('Program Terminated.')
    raise SystemExit
print("Rotating")
cmd = []
cmd.append(multiprocessing.Process(target=movment,
                                 args=(module_tmcm_1276[0], 30000, 4,)))
cmd.append(multiprocessing.Process(target=movment,
                                 args=(module_tmcm_1276[1], -151000, 2,)))

for item in cmd:
    item.start()

for item in cmd:
    item.join()


""" print("Stopping")
for tmcm in module_tmcm_1276:
    tmcm.stop() """

for interface in my_interface:
    interface.close()
