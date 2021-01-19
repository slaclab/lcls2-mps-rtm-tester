#!/usr/bin/env python

import sys
import getopt
import os
import subprocess
import socket

class SocketHanlder:
    """
    Class to handler the TCP socket.
    It provides a method to send a message and read back the response.
    """
    def __init__(self, ip_addr, port_number, terminator='@'):
        self.ip_addr     = ip_addr
        self.port_number = port_number
        self.terminator  = terminator
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((ip_addr, port_number))
        except socket.error as e:
            exit_message("ERROR: Can not connect to target: {}".format(e))

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

# Usage message
def usage(name):
    print("Usage: {} -a|--addr IP_address -p|--port port_number [-h|--help]".format(name))
    print("    -a|--addr IP_address : Target IP address")
    print("    -p|--port            : Target TCP port number")
    print("    -h|--help]           : Show this message")
    print("")

# Exit on error printing a message
def exit_message(message):
    print(message)
    print("")
    exit()

# Main body
if __name__ == '__main__':

    # Process input arguments.
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ha:p:",["ip-addr=", "port="])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)

    ip_addr     = ""
    port_number = 0

    for opt, arg in opts:
        if opt in ("-h","--help"):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ("-a","--ip-addr"):
            ip_addr = arg
        elif opt in ("-p", "--port"):
            try:
                port_number = int(arg)
            except ValueError:
                exit_message("ERROR: Invalid port number")

    try:
        socket.inet_aton(ip_addr)
    except socket.error:
        exit_message("ERROR: Invalid IP Address.")

    if port_number == 0:
        exit_message("ERROR: You must specify a port number.");

    # Check if the device is online
    print("")
    print("Trying to ping the target...")
    try:
       dev_null = open(os.devnull, 'w')
       subprocess.check_call(["ping", "-c2", ip_addr], stdout=dev_null, stderr=dev_null)
       print("    Target is online")
       print("")
    except subprocess.CalledProcessError:
       exit_message("    ERROR: Target can't be reached!")

    # Create a tester instance
    t = Tester(ip_addr=ip_addr, port_number=port_number)

    # Print the tester device information
    print("Target Firmware Information:")
    try:
        print(t.readInfo())
    except RuntimeError as e:
        print("readInfo() command return with an error code.")


    # Verify the RTM inputs
    print("Testing inputs channels...")
    in_ch_result = {}
    in_ch_error_cnt = 0
    in_ch_log = []
    for i in range(8):

        try:
            # Navigates all the inputs bits
            set_val = 2**i;

            # Write the value in the outputs of the tester device
            t.writeOutputs(set_val)

            # Read the values from the RTM inputs
            # get_val = rtm_in.getVal()
            get_val = set_val

            # Verify that the write and read value match
            # get_val == set_val?
            if i == 3 or i == 7:
                get_val = 0

            r = get_val == set_val

            #log result
            if r:
                m = "PASSED"
            else:
                m = "FAILED"
                in_ch_error_cnt += 1
                in_ch_log.append("Error in input channel {}. Set value was: {}, but read back value was {}.".format(i, set_val, get_val))

            in_ch_result[i] = m;

        except RuntimeError as e:
            print("writeOutputs({}) command failed on iteration {}.".format(val, i))
            # log result
        # handler cpsw exceptions

    print("Done!")
    print("")

    # Verify outputs
    print("Testing output channels...")
    out_ch_result = {}
    out_ch_error_cnt = 0
    out_ch_log = []
    for i in range(8):

        try:
            # Navigate all the output bits
            set_val = 2**i

            # Set the output value in the RTM
            # trm_out.setVal(set_val)

            # Read the values from the tester device
            get_val = t.readInputs()
            get_val = set_val

            # Verify that the write and read value match
            # get_val == set_val?
            if i == 5:
                get_val = 0;

            r = get_val == set_val

            # log result
            if r:
                m = "PASSED"
            else:
                m = "FAILED"
                out_ch_error_cnt += 1
                out_ch_log.append("Error in output channel {}. Set value was: {}, but read back value was {}.".format(i, set_val, get_val))

            out_ch_result[i] = m;

        except RuntimeError as e:
            print("readInputs() command failed on iteration {}.".format(i))
            # log result
        # handler cpsw exceptions

    print("Done!")
    print("")

    print("*************************")
    print("***   Test results:   ***")
    print("*************************")
    print("")

    print("Input Channels:")
    print("=============================")
    print("")

    print("---------------------")
    print("Channel | Test result")
    print("---------------------")
    for v,k in in_ch_result.items():
        print("   {:02}   | {}".format(v, k))
    print("---------------------")
    print("")

    print("Log:")
    print("-------------------------------")
    for log in in_ch_log:
        print(log)
    print("-------------------------------")
    print("")

    print("Number of Input Channel Fails: {}".format(in_ch_error_cnt))
    print("")

    print("Output Channels:")
    print("=============================")
    print("")

    print("---------------------")
    print("Channel | Test result")
    print("---------------------")
    for v,k in out_ch_result.items():
        print("   {:02}   | {}".format(v, k))
    print("---------------------")
    print("")

    print("Log:")
    print("-------------------------------")
    for log in out_ch_log:
        print(log)
    print("-------------------------------")
    print("")

    print("Number of Output Channels Fails: {}".format(out_ch_error_cnt))
    print("\n")