#!/usr/bin/env bash

# Import functions
. ./scripts/functions.sh

#############
# Main body #
#############

# Parse the inputs arguments.
arg_parser "$@"

# Get FPGA IP address
getFpgaIpAddr

# Firmware version checking
checkFW

if [ -z "${manual}" ]; then
    echo "using automatic test mode"
else
    echo "Using manual test mode"
fi