#!/usr/bin/env python3

from socket import gaierror
from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as oscm
from osc4py3 import oscbuildparse as oscbp
import time

class Client:
    """Based on: https://github.com/barlaensdoonn/osc_basics/blob/master/osc_basics.py"""
    def __init__(self, host: str, port: int, name: str) -> None:
        self.host = host
        self.port = port
        self.name = name
        self.start()

    def __enter__(self) -> 'Client':
        return self

    def start(self):
        osc_startup()
        try:
            osc_udp_client(self.host, self.port, self.name)
            print("OSC client ready.")
        except gaierror:
            print(
                "Host '{}' unavailable, failed to create client '{}'.".format(
                    self.host, 
                    self.name
                )
            )
            raise

    def send(self, address: str, data_types: str, data: str) -> None:
        message = oscbp.OSCMessage(
            address,
            data_types,
            data
        )
        osc_send(
            message,
            self.name
        )
        osc_process()
        print(str(message))

    def send_bundle(self, address: str, data_types: str, data: str) -> None:
        message_bundle = []
        for data_tuple in data:
            message_bundle.append(
                oscbp.OSCMessage(
                    address,
                    data_types,
                    [
                        str(data_tuple[0]),
                        data_tuple[1].x,
                        data_tuple[1].y,
                        data_tuple[1].z,
                        data_tuple[2].x,
                        data_tuple[2].y,
                        data_tuple[2].z,
                        data_tuple[2].w
                    ]
                )
            )
        message_bundle = oscbp.OSCBundle(
            oscbp.unixtime2timetag(time.time()),
            message_bundle
        )
        osc_send(
            message_bundle,
            self.name
        )
        osc_process()
        print(str(message_bundle))

    def __exit__(self, type, value, traceback) -> None:
        self.__del__()

    def __del__(self) -> None:
        osc_terminate()
        print("OSC client down.")
