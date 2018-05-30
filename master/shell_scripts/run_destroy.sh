#!/bin/bash
if [ "$do_not_destroy_vm" = "yes" ]; then
    echo "Config marked as undestroyable, exiting"
    exit 1
fi
if [ "$try_already_running" = "yes" ]; then
    echo "Config uses permanent VM, exiting"
    exit 1
fi

$HOME/mdbci/mdbci destroy $name