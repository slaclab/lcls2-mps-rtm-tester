#!/usr/bin/env bash

###############
# Definitions #
###############

# TOP directory, replacing the slac.stanford.edu soft link by slac
# which is not always present in the linuxRT CPUs
top_dir=$(dirname -- "$(readlink -f $0)" | sed 's/slac.stanford.edu/slac/g')

# This script name
script_name=$(basename $0)

# Shell PID
top_pid=$$

# Firmware file location
fw_top_dir="./firmware/ATCA/"

# Trap TERM signals and exit
trap "echo 'An ERROR was found. Check shelf manager & card state! Aborting...'; exit 1" TERM


########################
# Function definitions #
########################

# Import functions
. ./bash/functions.sh

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
