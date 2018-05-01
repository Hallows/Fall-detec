# usage: python multi_device [mac1] [mac2] ... [mac(n)]
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from gattlib import DiscoveryService
from time import sleep
from threading import Event

import platform
import sys

if sys.version_info[0] == 2:
    range = xrange

selection = -1

maclist = [] 

while selection == -1:
    service = DiscoveryService("hci0")
    devices = service.discover(2)
    i = 0
    for address, attr in devices.items():
        print("[%d] %s (%s)" % (i, address, attr['name']))
        i+= 1
    msg = "Select your device (-1 to rescan): "
    selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))

maclist.append(list(devices)[selection])
selection = -1

while selection == -1:
    service = DiscoveryService("hci0")
    devices = service.discover(2)
    i = 0
    for address, attr in devices.items():
        print("[%d] %s (%s)" % (i, address, attr['name']))
        i+= 1
    msg = "Select your another device (-1 to rescan): "
    selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))

maclist.append(list(devices)[selection])


print("save mac address as follows:",maclist[0],maclist[1])

class State:
    def __init__(self, device):
        self.device = device
        self.samples = 0
        self.callback = FnVoid_DataP(self.data_handler)

    def data_handler(self, data):
        print("%s -> %s" % (self.device.address, parse_value(data)))
        self.samples+= 1

states = []
print(len(maclist))

for z in range(0,1):
    print(maclist[z])
    d = MetaWear(maclist[z])
    d.connect()
    print("Connected to " + d.address)
    states.append(State(d))
    sleep(3.0)

print(len(states))

for s in states:
    print("configuring device")
    libmetawear.mbl_mw_settings_set_connection_parameters(s.device.board, 7.5, 7.5, 0, 6000)
    libmetawear.mbl_mw_acc_set_odr(s.device.board, 25.0);
    libmetawear.mbl_mw_acc_set_range(s.device.board, 16.0);
    libmetawear.mbl_mw_acc_write_acceleration_config(s.device.board);

    signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(s.device.board)
    libmetawear.mbl_mw_datasignal_subscribe(signal, s.callback)

    libmetawear.mbl_mw_acc_enable_acceleration_sampling(s.device.board);
    libmetawear.mbl_mw_acc_start(s.device.board);
    print("configuring ended")

sleep(5.0)

for s in states:
    libmetawear.mbl_mw_acc_stop(s.device.board)
    libmetawear.mbl_mw_acc_disable_acceleration_sampling(s.device.board)

    signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(s.device.board)
    libmetawear.mbl_mw_datasignal_unsubscribe(signal)
    libmetawear.mbl_mw_debug_disconnect(s.device.board)

sleep(1.0)

print("Total Samples Received")
for s in states:
    print("%s -> %d" % (s.device.address, s.samples))
