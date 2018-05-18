#!/bin/bash
coredumps=$($HOME/mdbci/scripts/build_parser/coredump_finder.sh $JOB_NAME-$BUILD_NUMBER url)
echo "COREDUMPS \\" > $WORKSPACE/coredumps_$BUILD_ID
if [[ -z "$coredumps" ]]; then
      echo "Coredumps was not found for build $BUILD_NUMBER" >> $WORKSPACE/coredumps_$BUILD_ID
else
      echo
      for coredump in $coredumps; do
          printf "$coredump \\\n" >> $WORKSPACE/coredumps_$BUILD_ID
      done
fi
cp $WORKSPACE/build_log_$BUILD_ID $HOME/LOGS/$JOB_NAME-$BUILD_ID/