#!/usr/bin/env python3

import curses


class AutomaticIOTester():
    """
    Test the RTM I/O channels, using the tester device.
    """

    def __init__(self, root, ip_addr, port_number):
        """
        initialize the object.
        """

        # The CPSW root device
        self.root = root

        # Create a tester device object
        from RtmTester.TesterDevice import TesterDevice

        self.tester_device = TesterDevice(
            ip_addr=ip_addr,
            port_number=port_number)

        # Print tester device firmware information
        print("Tester device firmware information:")
        try:
            print(self.tester_device.readInfo())
        except RuntimeError as e:
            print("readInfo() command returned with an error code. {}"
                  .format(e))
            raise

    def run_tests(self):
        """
        Run the tests.
        """

        print("##########################################")
        print("###    Start of Automatic I/O Tests    ###")
        print("##########################################")
        print("")

        # Verify the RTM inputs
        print("Testing inputs channels...")
        in_ch_result = {}
        in_ch_error_cnt = 0
        in_ch_log = []
        for i in range(8):

            try:
                # Navigates all the inputs bits
                set_val = 2**i

                # Write the value in the outputs of the tester device
                self.tester_device.writeOutputs(set_val)

                # Read the values from the RTM inputs
                # get_val = rtm_in.getVal()
                get_val = set_val

                # Verify that the write and read value match
                # get_val == set_val?
                if i == 3 or i == 7:
                    get_val = 0

                r = get_val == set_val

                # Log result
                if r:
                    m = "PASSED"
                else:
                    m = "FAILED"
                    in_ch_error_cnt += 1
                    in_ch_log.append("Error in input channel {}. Set value was: {}, \
                                     but read back value was {}."
                                     .format(i, set_val, get_val))

                in_ch_result[i] = m

            except RuntimeError as e:
                print("writeOutputs({}) command failed on iteration {}. {}"
                      .format(set_val, i, e))
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
                get_val = self.tester_device.readInputs()
                get_val = set_val

                # Verify that the write and read value match
                # get_val == set_val?
                if i == 5:
                    get_val = 0

                r = get_val == set_val

                # log result
                if r:
                    m = "PASSED"
                else:
                    m = "FAILED"
                    out_ch_error_cnt += 1
                    out_ch_log.append("Error in output channel {}. Set value was: \
                                      {}, but read back value was {}."
                                      .format(i, set_val, get_val))

                out_ch_result[i] = m

            except RuntimeError as e:
                print("readInputs() command failed on iteration {}. {}"
                      .format(i, e))
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
        for v, k in in_ch_result.items():
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
        for v, k in out_ch_result.items():
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

        print("")
        print("##########################################")
        print("###    End of Automatic I/O Tests      ###")
        print("##########################################")
        print("")


class ManualIOTester():
    """
    Test the RTM I/O channels, without using the tester device.
    """

    def __init__(self, root):
        """
        initialize the object.
        """

        self.root = root

        self.num_input_channels = 32
        self.num_output_channels = 8

        self.input_channel_index = list(range(self.num_input_channels))
        self.input_channel_state = [0]*self.num_input_channels
        self.input_channel_tested = ['N']*self.num_input_channels

        self.output_channel_index = list(range(self.num_output_channels))
        self.output_channel_state = [0]*self.num_output_channels
        self.output_channel_tested = ['N']*self.num_output_channels

    def run_tests(self):
        """
        Run the tests.
        """

        print("##########################################")
        print("###    Start of Manual I/O Tests       ###")
        print("##########################################")
        print("")

        # Set all output to 0 initially
        print("Setting all outputs to 0...                       ", end="")
        self.root.setRtmOutputWord(0)
        print("Done!")

        print("")
        input("Press a key to start the I/O testing...")
        curses.wrapper(self._main_curses)

        print("I/O test stopped.")

        print("")
        print("Test Summary:")
        print("")

        print("Input Channels:")
        print("=============================")

        print("Channel number | ", end="")
        for i in self.input_channel_index:
            print(f" {i:02} |", end="")
        print("")

        print("Tested         | ", end="")
        for i in self.input_channel_tested:
            if i == 'Y':
                color = "\033[92m"
            else:
                color = "\033[91m"
            print(f"  {color}{i}\033[0m |", end="")
        print("")

        print("")
        print("Output Channels:")
        print("=============================")
        print("Channel number | ", end="")
        for i in self.output_channel_index:
            print(f" {i:02} |", end="")
        print("")

        print("Tested         | ", end="")
        for i in self.output_channel_tested:
            if i == 'Y':
                color = "\033[92m"
            else:
                color = "\033[91m"
            print(f"  {color}{i}\033[0m |", end="")
        print("")

        # Set all output to 0 after the test
        print("Setting all outputs to 0...                       ", end="")
        self.root.setRtmOutputWord(0)
        print("Done!")

        print("")
        print("##########################################")
        print("###    End of Manual I/O Tests         ###")
        print("##########################################")
        print("")

    def _print_io_table(self, win):
        """
        Print the I/O state table.
        """
        win.addstr("Input Channels:\n")
        win.addstr("=============================\n")

        win.addstr("Channel number | ")
        for i in self.input_channel_index:
            win.addstr(f" {i:02} |")
        win.addstr("\n")

        win.addstr("Tested         | ")
        for i in self.input_channel_tested:
            win.addstr(f"  {i} |")
        win.addstr("\n")

        win.addstr("Current State  | ")
        for i in self.input_channel_state:
            win.addstr(f"  {i} |")
        win.addstr("\n")

        win.addstr("\n")
        win.addstr("Output Channels:\n")
        win.addstr("=============================\n")
        win.addstr("Channel number | ")
        for i in self.output_channel_index:
            win.addstr(f" {i:02} |")
        win.addstr("\n")

        win.addstr("Tested         | ")
        for i in self.output_channel_tested:
            win.addstr(f"  {i} |")
        win.addstr("\n")

        win.addstr("Current State  | ")
        for i in self.output_channel_state:
            win.addstr(f"  {i} |")
        win.addstr("\n")

        win.addstr("\n")
        win.addstr("Instructions:\n")
        win.addstr("-------------\n")
        win.addstr("Press a number between 0 and 7 to "
                   "toggle the corresponding output channel.\n")
        win.addstr("Press the ESC key to stop test\n")

    def _main_curses(self, win):
        """
        Main curses application.
        """
        win.timeout(1000)
        win.clear()
        self._print_io_table(win)
        while True:
            try:
                key = win.getkey()
                if key == '\x1b':
                    break
                else:
                    try:
                        ch = int(key)
                        if 0 <= ch <= 7:
                            # Toggle the output channel
                            new_val = not self.output_channel_state[ch]
                            self.root.setRtmOutputChannel(ch, value=new_val)
                            self.output_channel_state[ch] = int(new_val)
                            self.output_channel_tested[ch] = 'Y'

                            # Update the input states
                            self._update_input_states()

                            # Refresh the I/O table
                            win.clear()
                            self._print_io_table(win)

                    except ValueError:
                        pass
            except curses.error:
                # Update the input states
                self._update_input_states()

                # Refresh the I/O table
                win.clear()
                self._print_io_table(win)

    def _update_input_states(self):
        """
        Read the input state, and update the list of states.
        """

        pass
