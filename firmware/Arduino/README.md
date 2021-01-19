# Firmware for the RTM Tester Device

## Description

The RTM tester device is based on the [Arduino Mega 2560](https://store.arduino.cc/usa/mega-2560-r3). The firmware source code for this device in located in the [RtmTester](RtmTester) folder.

## Pre-requisites

### Arduino IDE

In order to compile the firmware and program the Arduino device, you need to install the `Arduino IDE` software, which is available [here](https://www.arduino.cc/en/software). Download and install the version compatible with your Operating System.

### Libraries

The `RtmTester` firmware uses the [Ethernet2](https://github.com/adafruit/Ethernet2) library. So, before you try to compile the firmware, you need to install it.

To install the library, open the IDE and click to the *Sketch* menu and then *Include Library* > *Manage Libraries*. Search for the *Ethernet2* library and click on *Install*.

More information about how to install libraries can be found [here](https://www.arduino.cc/en/Guide/Libraries).

## How program the Arduino device

* Connect the Arduino board to your PC or Laptop using an A/B USB
* Open the IDE, and click on the *File* menu and then *Open...*. Navigate to the location of the [RtmTester.ino](RtmTester/RtmTester.ino) file.
* Select you board type by clicking on the *Tools* menu and then *Board:* > *Arduino Mega or Mega 2560*.
* Select you port by clicking on the *Tools* menu and them *port* and selecting the serial device corresponding to the Arduino board. The serial device name is dynamic, and depends on you Operating System and PC or Laptop hardware configuration, but the serial port device has a description which indicates that correspond to the Arduino Mega 2560.
* Click on the *Sketch* menu, and then *Verify/Compile*, to verify that the firmware compiles without errors.
* Finally, upload the firmware to the Arduino device by clicking on the *Sketch* menu, and then *Upload*.