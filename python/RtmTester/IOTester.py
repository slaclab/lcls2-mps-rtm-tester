#!/usr/bin/env python3

class AutomaticIOTester():
    """
    Test the RTM I/O channels, using the tester device.
    """

    def __init__(self, root, ip_addr):
        """
        initialize the object.
        """

        self.root = root
        self.ip_addr = ip_addr

    def run_tests(self):
        """
        Run the tests.
        """

        print("##########################################")
        print("###    Start of Automatic I/O Tests    ###")
        print("##########################################")
        print("")

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
