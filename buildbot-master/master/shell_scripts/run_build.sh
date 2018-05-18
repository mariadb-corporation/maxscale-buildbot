#!/bin/bash
if [ ! -d ./BUILD/mdbci ] ; then
    mkdir default-maxscale-branch
    cd default-maxscale-branch
    git clone https://github.com/mariadb-corporation/MaxScale.git
    cd ..
fi
if [ ! -d ./BUILD ] ; then
    cp -r default-maxscale-branch/MaxScale/BUILD .
fi
if [ ! -d ./BUILD/mdbci ] ; then
    cp -r  default-maxscale-branch/MaxScale/BUILD/mdbci BUILD/
fi
./BUILD/mdbci/build.sh