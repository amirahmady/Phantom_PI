
from Phantom_Pi import *
from argparse import Namespace
import sys



def main(*args):
    my_interface =[0,0]
    module_tmcm_1276=[0,0]
    PyTrinamic.showInfo()
    connection_manager = ConnectionManager(
        argList=['--interface', args[0].connection, '--port','PCAN_USBBUS1','--module-id',"1",'--host-id','2'])
    my_interface[0] = connection_manager.connect()
    module_tmcm_1276[0] = TMCM_1276(my_interface[0])
    module_tmcm_1276[0].stop()

    connection_manager = ConnectionManager(
        argList=['--interface', args[0].connection,'--port','PCAN_USBBUS1', '--module-id',"3",'--host-id','2'])
    my_interface[0].close()
    my_interface[1] = connection_manager.connect()
    module_tmcm_1276[1] = TMCM_1276(my_interface[0])
    module_tmcm_1276[1].stop()
    print("motor stopped")
    lead = lead_per_pulse(256, 0.40, 'in')
    max_pps = unit_to_pulse(10, lead)
    #print(max_pps*4)
    end_stop_sw_status(module_tmcm_1276[0])
    #print(module_tmcm_1276[0]getAxisParameter(196))
    module_tmcm_1276[0].setGlobalParameter(82,0,1000)
    print('gp:',module_tmcm_1276[0].getGlobalParameter(0,2))
    print('ap:',module_tmcm_1276[0].getActualPosition())
    module_tmcm_1276[0].setGlobalParameter(0,2,10)

    i=0
    module_tmcm_1276[0].setMaxAcceleration(-100)
    while module_tmcm_1276[0].getMaxAcceleration()==0:
        module_tmcm_1276[0].setMaxAcceleration(-i)
        i=i+1
    #print(module_tmcm_1276[0]getMaxAcceleration())
    my_interface[1].close()
    my_interface[0] = connection_manager.connect()
    init_move_mm(module_tmcm_1276[0],lead)
    # module_tmcm_1276[0]rotate(100575)
    # time.sleep(3)
    module_tmcm_1276[0].stop()
    print("motor stopped") 
    #general_move(module_tmcm_1276)
    my_interface[0].close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arguments = parse_arguments()
    else:
        arguments = Namespace(connection='pcan_tmcl')
    main(arguments)
