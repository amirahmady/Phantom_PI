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



my_interface =[None,None]
module_tmcm_1276=[None,None]
connection_manager=[None,None]

PyTrinamic.showInfo()
connection_manager[0] = ConnectionManager(
    argList=['--interface', 'socketcan_tmcl','--module-id',"1",'--host-id','2'])
my_interface[0] = connection_manager[0].connect()
module_tmcm_1276[0] = TMCM_1276(my_interface[0])

connection_manager[1] = ConnectionManager(
    argList=['--interface', 'socketcan_tmcl', '--module-id',"4",'--host-id','5'])
my_interface[1] = connection_manager[1].connect()
module_tmcm_1276[1] = TMCM_1276(my_interface[1])
module_tmcm_1276[0].stop()
module_tmcm_1276[1].stop()

 


print("Preparing parameters")
for tmcm in module_tmcm_1276:
    tmcm.setMaxAcceleration(9000)

for tmcm in module_tmcm_1276:
    print('si',tmcm.getGlobalParameter(70,0))
    print('ri',tmcm.getGlobalParameter(71,0))
    print("2nd Motor:")




print("Stopping")
for tmcm in module_tmcm_1276:
    tmcm.stop()

temp=input("press return")

print("Rotating")

for tmcm in module_tmcm_1276:
    tmcm.rotate(+20000)

time.sleep(5)

print("Stopping")
for tmcm in module_tmcm_1276:
    tmcm.stop()

for interface in my_interface:
    interface.close()