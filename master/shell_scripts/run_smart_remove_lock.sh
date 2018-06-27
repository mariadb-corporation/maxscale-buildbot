#!/bin/bash
set -xe
lock_file=$HOME/vagrant_lock
if [ ! -e "$lock_file" ]; then
    exit 0
fi

locker=`cat $HOME/vagrant_lock`
if [ "$build_full_name" != "$locker" ]; then
    echo "Lock file was created not by current task! Lock file will not be removed."
    exit 1
fi

rm $HOME/vagrant_lock
if [ "$try_already_running" = "yes" ] ; then
    MDBCI_VM_PATH=${MDBCI_VM_PATH:-$HOME/vms}
    snapshot_lock_file=${MDBCI_VM_PATH}/${box}_snapshot_lock
    echo "Release lock for already running VM"
    rm -f $snapshot_lock_file
fi
