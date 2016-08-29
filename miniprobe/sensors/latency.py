#!/usr/bin/env python

import os
import gc
import logging

class Latency(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "latency"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Latency.get_kind(),
            "name": "Latency",
            "description": "Monitors the latency",
            "help": "Monitors the latency",
            "tag": "latencysensor",
            "groups": [
                {
                    "name": "Latency Settings",
                    "caption": "Latency Settings",
                    "fields": [
                        {
                            "type": "integer",
                            "name": "timeout",
                            "caption": "Timeout (in s)",
                            "required": "1",
                            "default": 60,
                            "minimum": 1,
                            "maximum": 300,
                            "help": "Timeout in seconds. A maximum value of 300 is allowed."
                        },
                        {
                            "type": "edit",
                            "name": "target_ip",
                            "caption": "Target IP adress",
                            "required": "1",
                            "help": "The IP adress of the target you want to monitore"
                        },
                        {
                            "type": "integer",
                            "name": "port",
                            "caption": "Port",
                            "required": "1",
                            "default": 50000,
                            "minimum": 1024,
                            "maximum": 65536,
                            "help": "Define the target and source port for Latency monitoring"
                        },
                        {
                            "type": "integer",
                            "name": "pingcount",
                            "caption": "Ping Count",
                            "required": "1",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 20,
                            "help": "Enter the number of ping request the probe will send to the device during an interval"
                        },
                        {
                            "type": "integer",
                            "name": "pingsize",
                            "caption": "Ping packet size",
                            "required": "1",
                            "default": 32,
                            "minimum": 1,
                            "maximum": 10000,
                            "help": "The default packet size for ping request is 32 bytes, "
                                    "but you can choose any other size between 1 and 10,000 bytes."
                        }
                    ]
                }
            ]
        }
        return sensordefinition

    def latency(self, target, pingcount, pingsize, port, timeout):
        ping = ""
        ret = os.popen("/bin/ping -c %s -s %s -W %s %s" % (str(pingcount), str(pingsize), str(timeout), str(target)))
        pingdata = ret.readlines()
        ret.close()
        for line in pingdata:
            if line.startswith("r"):
                ping = line.split("=")[1].lstrip()
        if ping == '':
            return "Not reachable!"
        values = ping.split("/")
        channel_list = [
            {
                "name": "Ping Time Min",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[0])
            },
            {
                "name": "Ping Time Avg",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[1])
            },
            {
                "name": "Ping Time Max",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[2])
            },
            {
                "name": "Ping Time MDEV",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[3].split(' ')[0])
            }
        ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        latency = Latency()
        try:
            latencydata = latency.latency(data['target_ip'], data['pingcount'], data['pingsize'], data['port'], data['timeout'])
            if latencydata == "Not reachable!":
                data_r = {
                    "sensorid": int(data['sensorid']),
                    "error": "Exception",
                    "code": 1,
                    "message": data['target_ip'] + " is " + latencydata
                }
            else:
                data_r = {
                    "sensorid": int(data['sensorid']),
                    "message": "OK",
                    "channel": latencydata
                }
            logging.debug("Runnign sensor: %s" % latency.get_kind())
            logging.debug("Host: %s Port: %s Timeout: %s" % (data['target_ip'],
                    data['port'], data['timeout']))
        except Exception as e:
            logging.error("Ooops something went wrong with '%s' sensor %s. Error: %s" % (latency.get_kind(), data['sensorid'], e))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Latency failed."
            }
            out_queue.put(data_r)
            return 1
        del latency
        gc.collect()
        out_queue.put(data_r)
        return 0
