#!/usr/bin/env python3

from pycpsw import Path, ScalVal, ScalVal_RO, YamlFixup


class CpswRoot():
    """
    CPSW Root Class.

    This class crates an interface to the ATCA AMC carrier FPGA register space,
    using CPSW, for testing the MPS RTM board.
    """
    def __init__(self, yaml_file, ip_addr, top_dev="NetIODev"):
        """
        Initialize object.
        """

        print(f"Connecting to FPGA (IP={ip_addr})...             ", end="")

        # Crate the CPSW root device
        self.root = Path.loadYamlFile(
            yaml_file,
            rootName=top_dev,
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

        print("Done!")

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
        if (channel < 0) or (channel > 7):
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
        self._setAndVerifyRtmOutputs(value=outputs)

    def setRtmOutputWord(self, value):
        """
        Set all the RTM output using a word.
        """

        # Check if the word is in range
        if (value < 0) or (value > 255):
            raise RuntimeError(f"Invalid output word value {value}")

        # Write and verify the outputs
        self._setAndVerifyRtmOutputs(value=value)

    def getRtmInputChannel(self, channel):
        """
        Get an RTM intput channel
        """

        # Check if the channel number is in range
        if channel not in range(33):
            raise RuntimeError(f"Invalid input channel number {channel}")

        # Convert the channel number to a mask
        mask = 1 << channel

        # Read the input channels word
        inputs = self.rtm_inputs.getVal()

        # Return the status of the selected channel
        return bool(inputs & mask)

    def getRtmInputWord(self):
        """
        Get all the RTM input word.
        """

        val = self.rtm_inputs.getVal()

        # Verify that the read word is in range
        if val >= 2**32:
            raise RuntimeError(f"ERROR: Read input word {val} is out of range")

        return val

    def _setAndVerifyRtmOutputs(self, value):
        """
        Write the output word and verify that the read-back matches.
        """

        # Write the outputs
        self.rtm_output.setVal(value)

        # Read back the output status
        readback = self.rtm_output_rbv.getVal()

        # Check if the read-back value matches with what we wrote
        if readback != value:
            raise RuntimeError("Outs were not set correctly. "
                               f"Set = {value}, read-back = {readback}")

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
