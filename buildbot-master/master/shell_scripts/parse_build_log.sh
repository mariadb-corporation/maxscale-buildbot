#!/bin/bash
$HOME/mdbci/scripts/build_parser/parse_ctest_log.rb  -l $WORKSPACE/build_log_$BUILD_ID -o $WORKSPACE/results_$BUILD_ID -r -f -j $WORKSPACE/json_$BUILD_ID -s $WORKSPACE/$JOB_NAME-$BUILD_ID/ctest_sublogs/
for i in $(ls "$WORKSPACE/$JOB_NAME-$BUILD_ID/ctest_sublogs/"); do
    mkdir -p $HOME/LOGS/$JOB_NAME-$BUILD_ID/LOGS/$i
    cp "$WORKSPACE/$JOB_NAME-$BUILD_ID/ctest_sublogs/$i/ctest_sublog" "$HOME/LOGS/$JOB_NAME-$BUILD_ID/LOGS/$i/"
done