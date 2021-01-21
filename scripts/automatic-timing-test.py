#!/usr/bin/env python3

import os
import sys

from RtmTester.CpswRoot import CpswRoot

# Calculate path to TOP YAML file
top_dir = os.path.dirname(sys.argv[0])
yaml_file = f'{top_dir}/../firmware/ATCA/' \
             'AmcCarrierMpsAnalogLinkNode_project.yaml/000TopLevel.yaml'

# Create the root device
r = CpswRoot(yaml_file=yaml_file)

# Set LCLS1 mode timing, and check if the link is up
print("Testing LCLS1 mode timing...  ")
r.setTimingLcls1mode()
if r.checkTimingLink():
    print("PASS\n")
else:
    print("FAILED\n")

# Set LCLS2 mode timing, and check if the link is up
print("Testing LCLS2 mode timing...  ")
r.setTimingLcls2mode()
if r.checkTimingLink():
    print("PASS\n")
else:
    print("FAILED\n")
