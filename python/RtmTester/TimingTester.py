#!/usr/bin/env python3

from RtmTester.Helpers import print_ok, print_failed


class TimingTester():
    """
    Test the RTM Timing inputs.
    """
    def __init__(self, rtm):
        """
        Initialize the object.
        """
        self.rtm = rtm

    def run_tests(self):
        """
        Run the tests.
        """

        print("########################################")
        print("###    Start of Timing Tests         ###")
        print("########################################")
        print("")

        print("Testing LCLS1 mode timing...  ", end="")
        self.rtm.setTimingLcls1mode()
        if self.rtm.checkTimingLink():
            print_ok("PASS")
        else:
            print_failed("FAILED")

        # Set LCLS2 mode timing, and check if the link is up
        print("Testing LCLS2 mode timing...  ", end="")
        self.rtm.setTimingLcls2mode()
        if self.rtm.checkTimingLink():
            print_ok("PASS")
        else:
            print_failed("FAILED")

        print("")
        print("########################################")
        print("###    End of Timing Tests           ###")
        print("########################################")
        print("")
