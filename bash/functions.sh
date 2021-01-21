#!/usr/bin/env bash

# Usage message
usage()
{
    echo "Test an MPS RTM board."
    echo ""
    echo "usage: ${script_name} [-S|--shelfmanager <shelfmanager_name> -N|--slot <slot_number>]"
    echo "                       [-c|--cpu <cpu_name>] [-m|--manual] [-D|--no-check-fw]"
    echo "    -S|--shelfmanager <shelfmanager_name> : ATCA shelfmanager node name or IP address."
    echo "    -N|--slot         <slot_number>       : ATCA crate slot number (2 to 7)."
    echo "    -c|--cpu          <cpu_name>          : CPU node name, connected to the ATCA crate."
    echo "    -m|--manual                           : Use manual test procedure (i.e. without the tester device)."
    echo "    -D|--no-check-fw                      : Disable FPGA version checking."
    echo "    -h|--help                             : Show this message."
    echo ""
    exit $1
}

# Parse the arguments
arg_parser()
{
    while [[ $# -gt 0 ]]
    do
        key="$1"

        case ${key} in
            -S|--shelfmanager)
            shelfmanager="$2"
            shift
            ;;
            -N|--slot)
            slot="$2"
            shift
            ;;
            -c|--cpu)
            cpu_name="$2"
            shift
            ;;
            -m|--manual)
            manual=1
            ;;
            -D|--no-check-fw)
            no_check_fw=1
            ;;
            -h|--help)
            usage 0
            ;;
            *)
            echo "Invalid argument! '$2'"
            usage 1
            ;;
        esac
        shift
    done

    # Verify mandatory parameters
    if [ -z "${shelfmanager}" ]; then
        echo "Shelfmanager not defined!"
        usage 1
    fi

    if [ -z "${slot}" ]; then
        echo "Slot number not defined!"
        usage 1
    fi

    if [ -z "${cpu_name}" ]; then
        echo "CPU name not defined!"
        usage 1
    fi

    if [ -z "${slot}" ]; then
        echo "Slot number not defined!"
        usage 1
    fi

    if [ ${slot} -lt 2 -o ${slot} -gt 7 ]; then
        echo "Invalid slot number! Must be a number between 2 and 7."
        exit 1
    fi

    # Verify that CPU is reachable
    checkNodeConnection ${cpu_name}

    # Verify that the shelfmanager is reachable
    checkNodeConnection ${shelfmanager}
}

getGitHashFW()
{
    local gh_inv
    local gh

    # Long githash (inverted)
    #gh_inv=$(ipmitool -I lan -H $shelfmanager -t $ipmb -b 0 -A NONE raw 0x34 0x04 0xd0 0x14  2> /dev/null)
    # Short githash (inverted)
    gh_inv=$(ipmitool -I lan -H $shelfmanager -t $ipmb -b 0 -A NONE raw 0x34 0x04 0xe0 0x04  2> /dev/null)

    if [ "$?" -ne 0 ]; then
        kill -s TERM ${top_pid}
    fi

    # Invert the string
    for c in ${gh_inv} ; do gh=${c}${gh} ; done

    # Return the short hash (7 bytes)
    echo ${gh} | cut -c 1-7
}

getGitHashMcs()
{
    local filename=$(basename $mcs_file_name)
    local gh=$(echo $filename | sed  -r 's/.+-+(.+).mcs.*/\1/')

    # Return the short hash (7 bytes)
    echo ${gh} | cut -c 1-7
}

getCrateId()
{
    local crate_id_str

    crate_id_str=$(ipmitool -I lan -H $shelfmanager -t $ipmb -b 0 -A NONE raw 0x34 0x04 0xFD 0x02 2> /dev/null)

    if [ "$?" -ne 0 ]; then
        kill -s TERM ${top_pid}
    fi

    local crate_id=`printf %04X  $((0x$(echo $crate_id_str | awk '{ print $2$1 }')))`

    if [ -z ${crate_id} ]; then
        kill -s TERM ${top_pid}
    fi

    echo ${crate_id}
}

getFpgaIp()
{
    # Calculate FPGA IP subnet from the crate ID
    local subnet="10.$((0x${crate_id:0:2})).$((0x${crate_id:2:2}))"

    # Calculate FPGA IP last octet from the slot number
    local fpga_ip="${subnet}.$(expr 100 + $slot)"

    echo ${fpga_ip}
}

# Get FPGA IP address
getFpgaIpAddr()
{
    ipmb=$(expr 0128 + 2 \* $slot)

    printf "Reading Crate ID via IPMI...                      "
    crate_id=$(getCrateId)
    echo "Create ID: ${crate_id}."

    printf "Calculating FPGA IP address...                    "
    fpga_ip=$(getFpgaIp)
    echo "FPGA IP: ${fpga_ip}."
}

# Check if firmware in FPGA matches MCS file
# Returns 0 if they match, or 1 otherwise.
checkFW()
{
    # Check if the firmware checking is disabled
    if [ -z ${no_check_fw+x} ]; then

        printf "Looking for mcs file...                           "
        mcs_file=$(find ${fw_top_dir} -maxdepth 1 -name *mcs*)
        if [ ! -f "${mcs_file}" ]; then
            echo "MCS file not found!."
            exit 1
        fi

        mcs_file_name=$(basename ${mcs_file})
        echo "Mcs file found: ${mcs_file_name}"

        printf "Reading FW Git Hash via IPMI...                   "
        fw_gh=$(getGitHashFW)
        echo "Firmware githash: '${fw_gh}'."

        printf "Reading MCS file Git Hash...                      "
        mcs_gh=$(getGitHashMcs)
        printf "MCS file githash: '${mcs_gh}'. "

        if [ "${fw_gh}" == "${mcs_gh}" ]; then
            echo "They match!."
        else
            echo "They don't match."
            echo "Loading image..."
            ProgramFPGA.bash -s ${shelfmanager} -n ${slot} -c ${cpu_name} -m ${mcs_file}
        fi
    else
        echo "Check firmware disabled."
    fi
}

# Check if the passed node is reachable.
# The node name is passed as the first argument.
# Exit with '1' if the node is not reachable.
checkNodeConnection()
{
    local node_name=$1

    # Check connection with cpu. Exit on error
    printf "Checking connection with ${node_name}...         "
    if ! ping -c 2 ${node_name} &> /dev/null ; then
        printf "Not reachable!\n"
        exit 1
    else
        printf "Connection OK!\n"
    fi
}

# Execute a command in the remote CPU.
# The command and arguments are passed as argument to this function.
executeRemoteCommand()
{
    ssh -x ${cpu_user_name}@${cpu_name} $@
}