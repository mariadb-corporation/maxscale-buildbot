#!/bin/bash
$HOME/mdbci/scripts/benchmark_parser/parse_log.rb -i $WORKSPACE/build_log_$BUILD_ID -e $WORKSPACE/env_results_$BUILD_ID -o $WORKSPACE/json_$BUILD_ID
