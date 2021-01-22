#!usr/bin/env python3

import argparse

from RtmTester.Rtm import Rtm
from RtmTester.TimingTester import TimingTester


def get_args():
    """
    Parse and return the inputs arguments.
    """
    parser = argparse.ArgumentParser(
        description='LCLS2 MPS RTM Test Application')

    parser.add_argument(
        '--yaml',
        type=str,
        required=True,
        dest='yaml_file',
        help='Path to the top level YAML file (000TopLevel.yaml)')

    parser.add_argument(
        '--ip-addr',
        type=str,
        required=True,
        dest='ip_addr',
        help='FPGA IP Address')

    parser.add_argument(
        '--root-name',
        type=str,
        default='NetIODev',
        dest='root_name',
        help='RTM CPSW root device name (default = "NetIODev")')

    parser.add_argument(
        '--manual',
        action='store_true',
        help='Use I/O manual test procedure (i.e. without the tester device)')

    return parser.parse_args()


if __name__ == '__main__':
    # Get input arguments
    args = get_args()

    # Crate CPSW rtm
    rtm = Rtm(
        yaml_file=args.yaml_file,
        ip_addr=args.ip_addr,
        root_name=args.root_name)

    print("Starting tests...")
    print("")

    # Do timing tests
    timing_tester = TimingTester(rtm=rtm)
    timing_tester.run_tests()

    # Do I/O tests
    if args.manual:
        # Manual testing
        from RtmTester.IOTester import ManualIOTester as IOTester

        io_tester = IOTester(rtm=rtm)
        io_tester.run_tests()

    else:
        # Automatic testing
        from RtmTester.IOTester import AutomaticIOTester as IOTester

        io_tester = IOTester(
            rtm=rtm,
            ip_addr='10.0.1.100',
            port_number=5000)
        io_tester.run_tests()
