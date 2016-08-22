#!/usr/bin/env python

import os
import gc
import logging

class MPLSLatency(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mplslatency"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": MPLSLatency.get_kind(),
            "name": "MPLS Latency",
            "description": "Monitors the latency of a MPLS",
            "help": "Monitors the latency of a MPLS",
            "tag": "mplslatencysensor",
            "groups": [
                {
                    "name": "MPLS Latency Settings",
                    "caption": "MPLS Latency Settings",
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
                        }
                    ]
                }
            ]
        }
        return sensordefinition

    def latency(self, target, port, timeout):
        latency = ""
        return "Not reachable!"

    @staticmethod
    def get_data(data, out_queue):
        latency = MPLSLatency()
        try:
            latencydata = latency.latency(data['target_ip'], data['port'], data['timeout'])
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
