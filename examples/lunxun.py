# usage: python multi_device [mac1] [mac2] ... [mac(n)]
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from gattlib import DiscoveryService
from time import sleep
from threading import Event
import numpy as np
from sklearn import svm
from sklearn.externals import joblib

import platform
import sys
import types

if sys.version_info[0] == 2:
    range = xrange

selection = -1

maclist = [] 

print("Loading Neural Network Model, please wait......")
clf = joblib.load('OSVM.pkl')
print("Neural Network Model Load SUCCESS!")

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

afile = open("acc.txt", "w")
gfile = open("gyo.txt", "w")

class aState:
    def __init__(self, device):
        self.device = device
        self.callback = FnVoid_DataP(self.data_handler)
    def data_handler(self, data):
        getdata=parse_value(data)
        gfile.write("%s\n" % getdata)
        result=str(getdata)
        temp=result.split( )
        ax=temp[2]
        ay=temp[5]
        ax=float(ax[:-1])+0.3
        ay=float(ay[:-1])+0.15
        print("x->%f y->%f"%(ax,ay))
        nninput=np.array([ax,ay])
        nninput=np.reshape(nninput,(-1,2))
        if clf.predict(nninput) > -1:
            print("Its Normal!")
        else:
            print("Warning!!!!")


class gState:
    def __init__(self, device):
        self.device = device
        self.callback = FnVoid_DataP(self.data_handler)

    def data_handler(self, data):
        #print("GYO -> %s" % (parse_value(data)))
        gfile.write("%s\n" % (parse_value(data)))

print("Connecting.....")

d = MetaWear(maclist[0])
d.connect()
print("Connected to ACC device at MAC:" + d.address)
a=aState(d)
sleep(0.5)

d = MetaWear(maclist[1])
d.connect()
print("Connected to GYO device at MAC:" + d.address)
g=gState(d)
sleep(0.5)


print("configuring device..........")
libmetawear.mbl_mw_settings_set_connection_parameters(a.device.board, 7.5, 7.5, 0, 6000)
libmetawear.mbl_mw_acc_set_odr(a.device.board, 25.0);
libmetawear.mbl_mw_acc_set_range(a.device.board, 16.0);
libmetawear.mbl_mw_acc_write_acceleration_config(a.device.board);

asignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(a.device.board)
libmetawear.mbl_mw_datasignal_subscribe(asignal, a.callback)

libmetawear.mbl_mw_acc_enable_acceleration_sampling(a.device.board);
libmetawear.mbl_mw_acc_start(a.device.board);
print("ACC config finished")

libmetawear.mbl_mw_settings_set_connection_parameters(g.device.board, 7.5, 7.5, 0, 6000)
libmetawear.mbl_mw_gyro_bmi160_set_odr(g.device.board, GyroBmi160Odr._25Hz);
libmetawear.mbl_mw_gyro_bmi160_set_range(g.device.board, GyroBmi160Range._500dps)
libmetawear.mbl_mw_gyro_bmi160_write_config(g.device.board)

gsignal = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(g.device.board)
libmetawear.mbl_mw_datasignal_subscribe(gsignal, g.callback)

libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(g.device.board)
libmetawear.mbl_mw_gyro_bmi160_start(g.device.board)
print("GYRO config finished")

sleep(10)

libmetawear.mbl_mw_datasignal_unsubscribe(asignal)
libmetawear.mbl_mw_datasignal_unsubscribe(gsignal)
libmetawear.mbl_mw_acc_stop(a.device.board)
libmetawear.mbl_mw_gyro_bmi160_stop(g.device.board)
libmetawear.mbl_mw_debug_disconnect(a.device.board)
libmetawear.mbl_mw_debug_disconnect(g.device.board)
print("Disconnected!")