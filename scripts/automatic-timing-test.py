#!/usr/bin/env python3


from RtmTester.CpswRoot import CpswRoot

# Create the root device
r = CpswRoot(yaml_file="")

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
