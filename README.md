# LCLS2 MPS RTM Tester

## Description

This repository contains tools and applications for testing the RTM boards used by the LCLS2 MPS project.

The top script to run the test is [test-rtm.sh](test-rtm.sh), and it usage is:

```bash
usage: test-rtm.sh [-S|--shelfmanager <shelfmanager_name> -N|--slot <slot_number>]
                       [-c|--cpu <cpu_name>] [-m|--manual] [-D|--no-check-fw]
    -S|--shelfmanager <shelfmanager_name> : ATCA shelfmanager node name or IP address.
    -N|--slot         <slot_number>       : ATCA crate slot number (2 to 7).
    -c|--cpu          <cpu_name>          : CPU node name, connected to the ATCA crate.
    -m|--manual                           : Use manual test procedure (i.e. without the tester device).
    -D|--no-check-fw                      : Disable FPGA version checking.
    -h|--help                             : Show this message.
```
