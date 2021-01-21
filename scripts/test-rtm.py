#!usr/bin/env python3

import argparse

from RtmTester.CpswRoot import CpswRoot
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
        dest='root_dev_name',
        help='Root device name (default = "NetIODev")')

    parser.add_argument(
        '--manual',
        action='store_true',
        help='Use I/O manual test procedure (i.e. without the tester device)')

    return parser.parse_args()


if __name__ == '__main__':
    # Get input arguments
    args = get_args()

    # Crate CPSW root
    root = CpswRoot(
        yaml_file=args.yaml_file,
        ip_addr=args.ip_addr,
        top_dev=args.root_dev_name)

    print("Starting tests...")
    print("")

    # Do timing tests
    timing_tester = TimingTester(root=root)
    timing_tester.run_tests()

    # Do I/O tests
    if args.manual:
        # Manual testing
        from RtmTester.IOTester import ManualIOTester as IOTester

        io_tester = IOTester(root=root)
        io_tester.run_tests()

    else:
        # Automatic testing
        from RtmTester.IOTester import AutomaticIOTester as IOTester

        io_tester = IOTester(root=root, ip_addr='192.168.1.1')
        io_tester.run_tests()
