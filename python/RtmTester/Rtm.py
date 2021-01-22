#!/usr/bin/env python3

from RtmTester.Helpers import print_ok, print_failed

from pycpsw import Path, ScalVal, ScalVal_RO, YamlFixup


class Rtm():
    """
    RTM interface class. It uses CPSW to access the RTM related register in the
    AMCc FPGA.

    This class crates an interface to the ATCA AMC carrier FPGA register space,
    using CPSW, for testing the MPS RTM board.
    """
    def __init__(self, yaml_file, ip_addr, root_name="NetIODev"):
        """
        Initialize object.
        """

        # Define the number of inputs and output
        self.num_inputs = 32
        self.num_outputs = 8

        print(f"Connecting to FPGA (IP={ip_addr})...             ", end="")

        # Crate the CPSW root
        self.root = Path.loadYamlFile(
            yaml_file,
            rootName=root_name,
            yamlFixup=self.FixupRoot(ip_addr=ip_addr))

        # Create interfaces to the timing related registers
        self.timing_clksel = ScalVal.create(
            self.root.findByName(
                "mmio/AmcCarrierCore/AmcCarrierTiming/TimingFrameRx/ClkSel"))
        self.timing_rxlinkup = ScalVal_RO.create(
            self.root.findByName(
                "mmio/AmcCarrierCore/AmcCarrierTiming/TimingFrameRx/RxLinkUp"))
        self.timing_outputconfig = ScalVal.create(
            self.root.findByName(
                "mmio/AmcCarrierCore/AxiSy56040/OutputConfig[1]"))

        # Create interfaces to the RTM I/O related registers
        self.rtm_output = ScalVal.create(
            self.root.findByName(
                "mmio/AppTop/AppCore/MpsLinkNodeCore/MpsDigitalMessage/"
                "OutputBits"))
        self.rtm_output_rbv = ScalVal_RO.create(
            self.root.findByName(
                "mmio/AppTop/AppCore/RtmMpsLinkNode/RtmDout"))
        self.rtm_inputs = ScalVal_RO.create(
            self.root.findByName(
                "mmio/AppTop/AppCore/RtmMpsLinkNode/RtmDin"))

        print_ok("Done!")

    def setTimingLcls1mode(self):
        """
        Configure the timing module to receive LCLS1 time.
        """

        self.timing_outputconfig.setVal('RTM_TIMING_IN0')
        self.timing_clksel.setVal(0)

    def setTimingLcls2mode(self):
        """
        Configure the timing module to receive LCLS2 time.
        """

        self.timing_outputconfig.setVal('RTM_TIMING_IN1')
        self.timing_clksel.setVal(1)

    def checkTimingLink(self):
        """
        Return if the timing link is up.
        """

        return bool(self.timing_rxlinkup.getVal())

    def setRtmOutputChannel(self, channel, value=True):
        """
        Set an RTM output channel
        """

        # Check if the channel number is in range
        if (channel < 0) or (channel > (self.num_outputs - 1)):
            raise RuntimeError(f"Invalid output channel number {channel}")

        # Convert the channel number to a mask
        mask = value << channel

        # Read the current status of the output word
        outputs = self.rtm_output.getVal()

        if value:
            # Set the bit corresponding to the channel
            outputs |= mask
        else:
            # Clear the bit corresponding to the channel
            outputs &= ~mask

        # Write and verify the updated value
        self.setRtmOutputWord(value=outputs)

    def setRtmOutputWord(self, value):
        """
        Set all the RTM output using a word.
        """

        # Check if the word is in range
        if (value < 0) or (value >= 2**self.num_outputs):
            raise RuntimeError(f"Invalid output word value {value}")

        # Write the outputs
        self.rtm_output.setVal(value)

        # Read back the output status
        readback = self.rtm_output_rbv.getVal()

        # Check if the read-back value matches with what we wrote
        if readback != value:
            raise RuntimeError("Outs were not set correctly. "
                               f"Set = {value}, read-back = {readback}")

    def getRtmInputChannel(self, channel):
        """
        Get an RTM intput channel
        """

        # Check if the channel number is in range
        if (channel < 0) or (channel >= self.num_inputs):
            raise RuntimeError(f"Invalid input channel number {channel}")

        # Convert the channel number to a mask
        mask = 1 << channel

        # Read the input channels word
        inputs = self.getRtmInputWord()

        # Return the status of the selected channel
        return bool(inputs & mask)

    def getRtmInputWord(self):
        """
        Get all the RTM input word.
        """

        val = self.rtm_inputs.getVal()

        # Verify that the read word is in range
        if (val < 0) or (val >= 2**self.num_inputs):
            raise RuntimeError(f"ERROR: Read input word {val} is out of range")

        return val

    def getRtmInputListBits(self):
        """
        Get all the RTM input as a list of bits.
        """

        # Read the input word
        w = self.getRtmInputWord()

        # Convert the word to a list of bits
        return [int(b) for b in bin(w)[2:].zfill(32)]

    class FixupRoot(YamlFixup):
        """
        YamlFixup class, use to override the IP address defined in YAML.
        """

        def __init__(self, ip_addr):
            """
            Initialize object.
            """

            YamlFixup.__init__(self)
            self.ip_addr = ip_addr

        def __call__(self, root, top):
            """
            Look for the 'ipAddr' node and override it.
            """

            ip_addr_node = self.findByName(root, "ipAddr")
            ip_addr_node.set(self.ip_addr)
