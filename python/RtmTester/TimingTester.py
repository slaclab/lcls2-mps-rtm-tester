#!/usr/bin/env python3

class TimingTester():
    """
    Test the RTM Timing inputs.
    """
    def __init__(self, root):
        """
        Initialize the object.
        """
        self.root = root

    def run_tests(self):
        """
        Run the tests.
        """
        print("########################################")
        print("###    Start of Timing Tests         ###")
        print("########################################")
        print("")

        print("Testing LCLS1 mode timing...  ", end="")
        self.root.setTimingLcls1mode()
        if self.root.checkTimingLink():
            print("PASS")
        else:
            print("FAILED")

        # Set LCLS2 mode timing, and check if the link is up
        print("Testing LCLS2 mode timing...  ", end="")
        self.root.setTimingLcls2mode()
        if self.root.checkTimingLink():
            print("PASS")
        else:
            print("FAILED")

        print("")
        print("########################################")
        print("###    End of Timing Tests           ###")
        print("########################################")
        print("")
