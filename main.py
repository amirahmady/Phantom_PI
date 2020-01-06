from __future__ import print_function

import canopen


def main():
    # bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)
    #
    # msg = can.Message(arbitration_id=0x304,
    #                   data=[0, 1, 2, 3, 4, 5, 6, 7])
    #
    # try:
    #     bus.send(msg)
    #     print("Message sent on {}".format(bus.channel_info))
    # except can.CanError:
    #     print("Message NOT sent")

    network = canopen.Network()
    network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=100000)
    node_id = 2
    node = network.add_node(node_id, 'TMCM-1276.eds')
    # node.sdo['Modes of operation'].raw = 0x02  # Set velocity mode
    # node.sdo['Polarity'].raw = 0x00  # Set clockwise
    # node.sdo['Peak current'].raw = 1000  # Set peak current to 1000mA
    # node.sdo['vl velocity acceleration'][2].raw = 2  # Set acceleration
    # node.sdo['vl velocity deceleration'][2].raw = 1  # Set deceleration
    #
    # node.sdo['Controlword'].raw = 0x0  # Set DS402 Power State machine
    # node.sdo['Controlword'].raw = 0x80
    # node.sdo['Controlword'].raw = 0x06
    # node.sdo['Controlword'].raw = 0x07
    # node.sdo['Controlword'].raw = 0x0f
    print('run')
    # for obj in node.object_dictionary.values():
    #     print('0x%X: %s' % (obj.index, obj.name))
    #     if isinstance(obj, canopen.objectdictionary.Record):
    #         for subobj in obj.values():
    #             print('  %d: %s' % (subobj.subindex, subobj.name))
    # vendor_id_obj = node.object_dictionary[0x1018][1]
    # device_type = node.object_dictionary[0x1018][2]

    # Read current PDO configuration
    network.sync.start(0.01)
    network.sync.start(0.01)
    node.tpdo.read()
    node.rpdo.read()

    # Save new configuration (node must be in pre-operational)
    node.nmt.state = 'PRE-OPERATIONAL'
    node.tpdo.save()
    node.rpdo.save()

    print(vendor_id_obj, device_type)


if __name__ == "__main__":
    main()
