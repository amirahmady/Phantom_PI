
from Phantom_Pi import *
from argparse import Namespace
import sys



def main(*args):
    PyTrinamic.showInfo()
    connection_manager = ConnectionManager(
        argList=['--interface', args[0].connection])
    my_interface = connection_manager.connect()
    module_tmcm_1276 = TMCM_1276(my_interface)
    module_tmcm_1276.stop()
    print("motor stopped")
    lead = lead_per_pulse(256, 0.40, 'in')
    max_pps = unit_to_pulse(10, lead)
    #print(max_pps*4)
    end_stop_sw_status(module_tmcm_1276)
    #print(module_tmcm_1276.getAxisParameter(196))
    module_tmcm_1276.setGlobalParameter(82,0,1000)
    print('gp:',module_tmcm_1276.getGlobalParameter(0,2))
    print('ap:',module_tmcm_1276.getActualPosition())
    module_tmcm_1276.setGlobalParameter(0,2,10)

    i=0
    module_tmcm_1276.setMaxAcceleration(-100)
    while module_tmcm_1276.getMaxAcceleration()==0:
        module_tmcm_1276.setMaxAcceleration(-i)
        i=i+1
    #print(module_tmcm_1276.getMaxAcceleration())
    init_move_mm(module_tmcm_1276,lead)
    # module_tmcm_1276.rotate(100575)
    # time.sleep(3)
    module_tmcm_1276.stop()
    print("motor stopped") 
    general_move(module_tmcm_1276)
    my_interface.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arguments = parse_arguments()
    else:
        arguments = Namespace(connection='pcan_tmcl')
    main(arguments)
