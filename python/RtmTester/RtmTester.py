#!/usr/bin/env python

import socket


class SocketHanlder:
    """
    Class to handler the TCP socket.
    It provides a method to send a message and read back the response.
    """
    def __init__(self, ip_addr, port_number, terminator='@'):
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

    # Send message and read response
    def send(self, msg):

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


class Tester:
    """
    Class to communicate with the target tester device.
    It provides methods to write the outputs, read the inputs and
    get the device information.
    """
    def __init__(self, ip_addr, port_number):
        self.socket = SocketHanlder(ip_addr, port_number)

    # Generic method used to send a command and process the response.
    def sendCommand(self, command):

        # Add terminator
        command += '\n'

        # Send command and read response
        r = self.socket.send(command)

        # Check if command was execute successfully. Raise an exception if not.
        if not r.startswith('0'):
            raise RuntimeError("Error on command execution")

        # return the response message without the error code.
        return r[1:]

    # Command to write the outputs
    def writeOutputs(self, val):
        self.sendCommand('=' + str(val))

    # Command to read the inputs
    def readInputs(self):
        try:
            return int(self.sendCommand('?'))
        except ValueError:
            raise RuntimeError("Not-numeric value received")

    # Command to get the device information
    def readInfo(self):
        return self.sendCommand('i')
