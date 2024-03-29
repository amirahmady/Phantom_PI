#!/usr/bin/env python
# coding: utf-8

"""
This example shows how sending a single message works.
"""

from __future__ import print_function

import can


def send_one():
    # this uses the default configuration (for example from the config file)
    # see https://python-can.readthedocs.io/en/stable/configuration.html
    # bus = can.interface.Bus()

    # Using specific buses works similar:
    # bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=250000)
    bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=250000)

    # bus = can.interface.Bus(bustype='ixxat', channel=0, bitrate=250000)
    # bus = can.interface.Bus(bustype='vector', app_name='CANalyzer', channel=0, bitrate=250000)
    # ...

    msg = can.Message(
        arbitration_id=0xC0FFEE, data=[0, 25, 0, 1, 3, 1, 4, 1], is_extended_id=True
    )

    try:
        bus.send(msg)
        print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message NOT sent")


if __name__ == "__main__":
    send_one()
