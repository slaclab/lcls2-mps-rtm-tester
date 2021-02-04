#!/usr/bin/env python3

import curses

from RtmTester.Helpers import print_ok, print_failed


class AutomaticIOTester():
    """
    Test the RTM I/O channels, using the tester device.
    """

    def __init__(self, rtm, ip_addr, port_number):
        """
        initialize the object.
        """

        # The RTM device
        self.rtm = rtm

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
            print(f"readInfo() command returned with an error code. {e}")
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
                get_val = self.rtm.getRtmInputWord()

                # Verify that the write and read value match
                r = (get_val == set_val)

                # Log result
                if r:
                    m = "PASSED"
                else:
                    m = "FAILED"
                    in_ch_error_cnt += 1
                    in_ch_log.append(f"Error in input channel {i}. \
                                     Set value was: {set_val}, \
                                     but read back value was {get_val}.")

                in_ch_result[i] = m

            except RuntimeError as e:
                print(f"writeOutputs({set_val}) or getRtmInputWord() command "
                      f"failed on iteration {i}. {e}")
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
                self.rtm.setRtmOutputWord(value=set_val)

                # Read the values from the tester device
                get_val = self.tester_device.readInputs()

                # Verify that the write and read value match
                r = (get_val == set_val)

                # log result
                if r:
                    m = "PASSED"
                else:
                    m = "FAILED"
                    out_ch_error_cnt += 1
                    out_ch_log.append(f"Error in output channel {i}. \
                                      Set value was: {set_val}, \
                                      but read back value was {get_val}.")

                out_ch_result[i] = m

            except RuntimeError as e:
                print(f"readInputs() or setRtmOutputWord({set_val}) command "
                      f"failed on iteration {i}. {e}")
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
            print(f"   {v:02}   | {k}")
        print("---------------------")
        print("")

        print("Log:")
        print("-------------------------------")
        for log in in_ch_log:
            print(log)
        print("-------------------------------")
        print("")

        print(f"Number of Input Channel Fails: {in_ch_error_cnt}")
        print("")

        print("Output Channels:")
        print("=============================")
        print("")

        print("---------------------")
        print("Channel | Test result")
        print("---------------------")
        for v, k in out_ch_result.items():
            print(f"   {v:02}   | {k}")
        print("---------------------")
        print("")

        print("Log:")
        print("-------------------------------")
        for log in out_ch_log:
            print(log)
        print("-------------------------------")
        print("")

        print(f"Number of Output Channels Fails: {out_ch_error_cnt}")
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

    def __init__(self, rtm):
        """
        initialize the object.
        """

        self.rtm = rtm

        self.num_input_channels = 32
        self.num_output_channels = 8

        self.input_channel_index = list(range(self.num_input_channels))
        self.input_channel_state = self.rtm.getRtmInputListBits()
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
        self.rtm.setRtmOutputWord(0)
        print_ok("Done!")

        print("")
        input("Press ENTER to start the I/O testing...")
        curses.wrapper(self._main_curses)

        print("I/O test stopped.")

        print("")
        print("Test Summary:")
        print("")

        print("Input Channels:")
        print("=============================")

        n = 2
        for j in range(n):
            start = j * self.num_input_channels // n
            stop = start + self.num_input_channels // n

            print("Channel number | ", end="")
            for i in self.input_channel_index[start:stop]:
                print(f" {i:02} |", end="")
            print("")

            print("Tested         | ", end="")
            for i in self.input_channel_tested[start:stop]:
                if i == 'Y':
                    print_ok(f"  {i}", end="")
                else:
                    print_failed(f"  {i}", end="")
                print(" |", end="")
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
                print_ok(f"  {i}", end="")
            else:
                print_failed(f"  {i}", end="")
            print(" |", end="")
        print("")

        # Set all output to 0 after the test
        print("")
        print("Setting all outputs to 0...                       ", end="")
        self.rtm.setRtmOutputWord(0)
        print_ok("Done!")

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

        n = 2
        for j in range(n):
            start = j * self.num_input_channels // n
            stop = start + self.num_input_channels // n

            win.addstr("Channel number | ")
            for i in self.input_channel_index[start:stop]:
                win.addstr(f" {i:02} |")
            win.addstr("\n")

            win.addstr("Tested         | ")
            for i in self.input_channel_tested[start:stop]:
                win.addstr(f"  {i}", curses.color_pair(
                    self.green if i == "Y" else self.red))
                win.addstr(" |")
            win.addstr("\n")

            win.addstr("Current State  | ")
            for i in self.input_channel_state[start:stop]:
                win.addstr(f"  {i}", curses.color_pair(
                    self.magenta if i else self.blue))
                win.addstr(" |")
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
            win.addstr(f"  {i}", curses.color_pair(
                self.green if i == "Y" else self.red))
            win.addstr(" |")
        win.addstr("\n")

        win.addstr("Current State  | ")
        for i in self.output_channel_state:
            win.addstr(f"  {i}", curses.color_pair(
                self.magenta if i else self.blue))
            win.addstr(" |")
        win.addstr("\n")

        win.addstr("\n")
        win.addstr("Instructions:\n")
        win.addstr("-------------\n")
        win.addstr("- The 'Input Channels' section shows the state of the "
                   "input channels in real time.\n")
        win.addstr("  Change the physical input signal between high and low "
                   "levels and verify that the corresponding\n")
        win.addstr("  state changes accordingly in this table. Test one "
                   "channel at a time.\n")
        win.addstr("  The row 'Tested' shows which channel has changed state "
                   "during this test.\n")
        win.addstr("- The 'Output Channels' section shows the current state"
                   "of the output channels in real time.\n")
        win.addstr("  Press a key number between 0 and 7 to toggle the "
                   "corresponding output channel. Verify that the\n")
        win.addstr("  physical output level changes accordingly. Test one "
                   "channel at a time.\n")
        win.addstr("  The row 'Tested' shows which channel has changed state "
                   "during this test.\n")
        win.addstr("- The table is refreshed every second.\n")
        win.addstr("- After testing all channel, press the 'ESC' key to stop "
                   "the test.\n")
        win.addstr("  A summary will be presented at the end.\n")

    def _main_curses(self, win):
        """
        Main curses application.
        """
        curses.start_color()
        curses.use_default_colors()
        self.green = 1
        self.red = 2
        self.magenta = 3
        self.blue = 4
        curses.init_pair(self.green,   2, -1)  # 'Y' color, green
        curses.init_pair(self.red,     1, -1)  # 'N' color, red
        curses.init_pair(self.magenta, 5, -1)  # '1' color, magenta
        curses.init_pair(self.blue,    4, -1)  # '0' color, blue
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
                            new_val = self.output_channel_state[ch] ^ 1
                            self.rtm.setRtmOutputChannel(ch, value=new_val)
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
        Read the inputs and update the state and tested lists.
        """

        # Read the input states
        new_inputs = self.rtm.getRtmInputListBits()

        # Update the tested list
        for i in range(self.num_input_channels):
            if new_inputs[i] != self.input_channel_state[i]:
                self.input_channel_tested[i] = 'Y'

        # Update the input state list
        self.input_channel_state = new_inputs
