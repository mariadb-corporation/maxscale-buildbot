#!/bin/bash
$HOME/mdbci/scripts/build_parser/write_build_results.rb -f $WORKSPACE/json_$BUILD_ID; exit `cat result_$BUILD_ID`