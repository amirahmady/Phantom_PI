
from Phantom_Pi import *
from argparse import Namespace
import sys



def main(*args):
    PyTrinamic.showInfo()
    module_tmcm_1276=list(range(3))
    connection_manager = ConnectionManager(
        argList=['--interface', args[0].connection, '--module-id',"2",'--host-id','4'])
    my_interface = connection_manager.connect()
    module_tmcm_1276[0] = TMCM_1276(my_interface)
    module_tmcm_1276[0].stop()
    print("motor stopped")
    lead = lead_per_pulse(256, 0.40, 'in')
    max_pps = unit_to_pulse(10, lead)
    #print(max_pps*4)
    end_stop_sw_status(module_tmcm_1276[0])
    #print(module_tmcm_1276[0].getAxisParameter(196))
    module_tmcm_1276[0].setGlobalParameter(82,0,1000)
    print('gp:',module_tmcm_1276[0].getGlobalParameter(0,2))
    print('ap:',module_tmcm_1276[0].getActualPosition())
    module_tmcm_1276[0].setGlobalParameter(0,2,10)

    i=0
    module_tmcm_1276[0].setMaxAcceleration(-100)
    while module_tmcm_1276[0].getMaxAcceleration()==0:
        module_tmcm_1276[0].setMaxAcceleration(-i)
        i=i+1
    #print(module_tmcm_1276[0].getMaxAcceleration())
    init_move_mm(module_tmcm_1276[0],lead)
    # module_tmcm_1276[0].rotate(100575)
    # time.sleep(3)
    module_tmcm_1276[0].stop()
    print("motor stopped") 
    general_move(module_tmcm_1276[0])
    my_interface.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arguments = parse_arguments()
    else:
        arguments = Namespace(connection='pcan_tmcl')
    main(arguments)
