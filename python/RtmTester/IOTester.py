#!/usr/bin/env python3

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
        from RtmTester.RtmTester import TesterDevice

        print("Connecting to tester dev ({ip_addr}:{port_number})...  ",
              end="")

        self.tester_device = TesterDevice(
            ip_addr=ip_addr,
            port_number=port_number)

        print("Done!")

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

    def run_tests(self):
        """
        Run the tests.
        """

        print("##########################################")
        print("###    Start of Manual I/O Tests       ###")
        print("##########################################")
        print("")

        print("")
        print("##########################################")
        print("###    End of Manual I/O Tests         ###")
        print("##########################################")
        print("")
