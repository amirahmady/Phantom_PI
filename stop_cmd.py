
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
    end_stop_sw_status(module_tmcm_1276)
    print(module_tmcm_1276.getAxisParameter(140))
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
