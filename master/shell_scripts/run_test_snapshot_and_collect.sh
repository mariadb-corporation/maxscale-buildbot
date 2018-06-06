#!/bin/bash
if [ ! -d ./maxscale-system-test/mdbci ] ; then
    mkdir default-maxscale-branch
    cd default-maxscale-branch
    git clone https://github.com/mariadb-corporation/MaxScale.git
    cd ..
    cp -r default-maxscale-branch/MaxScale/maxscale-system-test/mdbci maxscale-system-test/
fi
export no_vm_revert="no"
maxscale-system-test/mdbci/run_test_snapshot.sh | tee $WORKSPACE/build_log_$BUILD_ID; echo ${PIPESTATUS[0]} > result_$BUILD_ID