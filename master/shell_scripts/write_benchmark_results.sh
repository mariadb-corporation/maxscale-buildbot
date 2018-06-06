#!/bin/bash
$HOME/mdbci/scripts/benchmark_parser/write_benchmark_results.rb -i $WORKSPACE/json_$BUILD_ID -e $WORKSPACE/env_results_$BUILD_ID ; exit `cat $WORKSPACE/result_$BUILD_ID`
