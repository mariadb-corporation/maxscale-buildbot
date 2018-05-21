#!/bin/bash
locker=`cat $HOME/vagrant_lock`
if [ "$build_full_name" != "$locker" ]; then
    echo "Lock file was created not by current task! Lock file will not be removed."
    exit 1
fi