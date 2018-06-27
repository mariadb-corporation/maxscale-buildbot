#!/bin/bash
set -xe

if [ "$try_already_running" = "yes" ] ; then
    snapshot_lock_file=${MDBCI_VM_PATH}/${box}_snapshot_lock
    echo "Release lock for already running VM"
    rm -f $snapshot_lock_file
    exit 0
fi

lock_file=$HOME/vagrant_lock

if [ ! -e "$lock_file" ]; then
    exit 0
fi

locker=`cat $HOME/vagrant_lock`
if [ "$build_full_name" != "$locker" ]; then
    echo "Lock file was created not by current task! Lock file will not be removed."
    exit 0
fi

rm $HOME/vagrant_lock
