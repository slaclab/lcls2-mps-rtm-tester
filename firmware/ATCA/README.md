# Firmware for the ATCA AMC Carrier FPGA

## Description

In order to test an MPS RTM board, it has to be installed in an ATCA crate, with a AMC Carrier board. This folder contains the firmware image used by the AMC Carrier board FPGA: [AmcCarrierMpsAnalogLinkNode-0x00000013-20171219215836-rherbst-0a449c20.mcs.gz](AmcCarrierMpsAnalogLinkNode-0x00000013-20171219215836-rherbst-0a449c20.mcs.gz).

## How to program the FPGA

The carrier and RTM have to be installed in an ATCA crate in the LCLSDEV network, accessible from the `lcls-dev3` host.

To load the firmware image, login to `lcls-dev3`, clone this repository in AFS space, got to this directory, and then use the [ProgramFPGA.bash](https://github.com/slaclab/ProgramFPGA) script:
```bash
$  ProgramFPGA.bash --shelfmanager shelfmanager_name --slot slot_number -cpu cpu_name --mcs ./AmcCarrierMpsAnalogLinkNode-0x00000013-20171219215836-rherbst-0a449c20.mcs.gz
```

where:
- `shelfmanager_name` is the node name or IP address of the ATCA crate shelfmanager,
- `slot_number` is the the slot number where the AMC carrier is installed, and
- `cpu_name` is the node name of the CPU connected to the ATCA crate.