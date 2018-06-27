#!/bin/bash
set -xe
rm -f $HOME/vagrant_lock
if [ "$try_already_running" = "yes" ] ; then
    MDBCI_VM_PATH=${MDBCI_VM_PATH:-$HOME/vms}
    snapshot_lock_file=${MDBCI_VM_PATH}/${box}_snapshot_lock
    echo "Release lock for already running VM"
    rm -f $snapshot_lock_file
fi
