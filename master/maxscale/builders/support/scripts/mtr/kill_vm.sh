#!/bin/bash

export MDBCI_VM_PATH=/$HOME//vms/
export PATH=$PATH:/$HOME/mdbci/
machine_name=${Image}-${target}-${buildnumber}
echo ${machine_name}
mdbci destroy ${machine_name}


