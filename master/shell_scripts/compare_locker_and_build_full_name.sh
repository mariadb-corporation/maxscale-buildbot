#!/bin/bash
locker=`cat $MDBCI_VM_PATH/${name}_snapshot_lock`
if [ "$build_full_name" != "$locker" ]; then
    echo "Snapshot lock file was created not by current task! Lock file will not be removed."
    exit 1
fi