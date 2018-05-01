from mbientlab.metawear import MetaWear,libmetawear
from mbientlab.metawear.cbindings import *
from gattlib import DiscoveryService
from time import sleep
from threading import Event

import platform

selection = -1
devices = None

while selection == -1:
    service = DiscoveryService("hci0")
    devices = service.discover(2)

    i = 0
    for address, attr in devices.items():
        print("[%d] %s (%s)" % (i, address, attr['name']))
        i+= 1

    msg = "Select your device (-1 to rescan): "
    selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))

address = list(devices)[selection]
print("Connecting to %s..." % (address))
device = MetaWear(address)
device.connect()

print("Connected")
print("Device information: " + str(device.info) + "\n")
sleep(3.0)

print("start LED process")
pattern= LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.GREEN)
libmetawear.mbl_mw_led_play(device.board)

sleep(3.0)

libmetawear.mbl_mw_led_stop_and_clear(device.board)
sleep(1.0)

device.disconnect()
sleep(1.0)

