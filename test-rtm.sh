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
fw_top_dir=${top_dir}/firmware/ATCA/

# YAML Top file
yaml_top=${fw_top_dir}/AmcCarrierMpsAnalogLinkNode_project.yaml/000TopLevel.yaml

# Remote CPU user name
cpu_user_name=laci

# CPSW top directory
cpsw_top_dir=/afs/slac/g/lcls/package/cpsw/framework

# CPSW version
cpsw_version=R4.4.2

# CPSW env script
cpsw_env_script=${cpsw_top_dir}/${cpsw_version}/env.slac.sh

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

# Run the Timing test
executeRemoteCommand \
	"export PYTHONPATH=${top_dir}/python/:${PYTHONPATH} && \
        . ${cpsw_env_script} > /dev/null && \
	python3 ${top_dir}/scripts/test-rtm.py --yaml ${yaml_top} --ip-addr ${fpga_ip}"

if [ -z "${manual}" ]; then
    echo "using automatic test mode"
else
    echo "Using manual test mode"
fi
