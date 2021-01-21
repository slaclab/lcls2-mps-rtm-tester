#!/usr/bin/env python

import os
import subprocess
import socket


class TesterDevice:
    """
    Class to communicate with the target tester device.
    It provides methods to write the outputs, read the inputs and
    get the device information.
    """

    def __init__(self, ip_addr, port_number):
        """
        Initialize object.
        """

        # Check if the IP address is valid
        try:
            socket.inet_aton(ip_addr)
        except socket.error:
            print(f"ERROR: Invalid tester device IP address. {ip_addr}")
            raise

        # Check if the tester device is online
        print("Trying to ping the tester device...               ", end="")
        try:
            dev_null = open(os.devnull, 'w')
            subprocess.check_call(["ping", "-c2", ip_addr],
                                  stdout=dev_null,
                                  stderr=dev_null)
            print("\033[92mDevice is online!\033[0m")
        except subprocess.CalledProcessError:
            print("\033[91mERROR: Device is off-line!\033[0m")
            raise RuntimeError("Tester device can't be reach!")

        # Connect to the tester device
        print("Connecting to tester device...                    ", end="")
        self.socket = self.SocketHanlder(ip_addr, port_number)

    def sendCommand(self, command):
        """
        Generic method used to send a command and process the response.
        """

        # Add terminator
        command += '\n'

        # Send command and read response
        r = self.socket.send(command)

        # Check if command was execute successfully. Raise an exception if not.
        if not r.startswith('0'):
            raise RuntimeError("Error on command execution")

        # return the response message without the error code.
        return r[1:]

    def writeOutputs(self, val):
        """
        Command to write the outputs.
        """

        self.sendCommand('=' + str(val))

    def readInputs(self):
        """
        Command to read the inputs.
        """

        try:
            return int(self.sendCommand('?'))
        except ValueError:
            raise RuntimeError("Not-numeric value received")

    def readInfo(self):
        """
        Command to get the device information.
        """

        return self.sendCommand('i')

    class SocketHanlder:
        """
        Inner class to handler the TCP socket.
        It provides a method to send a message and read back the response.
        """

        def __init__(self, ip_addr, port_number, terminator='@'):
            """
            Initialize the object.
            """

            self.ip_addr = ip_addr
            self.port_number = port_number
            self.terminator = terminator
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self.socket.connect((ip_addr, port_number))
            except socket.error as e:
                print("ERROR: Can not connect to target: {}".format(e))
                raise

            print("Connected to {}.{}".format(ip_addr, port_number))

        def send(self, msg):
            """
            Send message and read response.
            """

            send_size = len(msg)
            total_sent = 0

            # Send command
            while total_sent < send_size:
                sent = self.socket.send(msg)

                # Check if connection is broken
                if sent == 0:
                    raise RuntimeError("Socket connection broken")

                # Keep sending until all message is sent
                total_sent = total_sent + sent

            # Read response
            response = ""
            while True:
                r = self.socket.recv(1024)

                # Check if connection is broken
                if r == b'':
                    raise RuntimeError("Socket connection broken")

                response += r

                # Keep reading until terminator is found
                if r.endswith(self.terminator):
                    # Remove terminator from response
                    response = response[:-1]
                    break

            return response
