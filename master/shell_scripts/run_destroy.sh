#!/bin/bash
set -xe
if [ "$do_not_destroy_vm" = "yes" ]; then
    echo "Config marked as undestroyable, exiting"
    exit 1
fi
if [ "$try_already_running" = "yes" ]; then
    echo "Config uses permanent VM, exiting"
    exit 1
fi

mdbci_config=$MDBCI_VM_PATH/$name
if [ ! -e "$mdbci_config" ]; then
    exit 0
fi

$HOME/mdbci/mdbci destroy $mdbci_config
