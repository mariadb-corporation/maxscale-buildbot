#!/bin/bash
cd ~/maxscale-performance-test
./bin/performance_test -v --server-config=~/performance_test_servers/performance-test_network_config --remote-test-app tests/run_sysbench.sh --db-server-2-config slave-config.sql.erb --db-server-3-config slave-config.sql.erb --db-server-4-config slave-config.sql.erb --mariadb-version $version --maxscale-config base.cnf.erb --maxscale-version $target --keep-servers true | tee $WORKSPACE/build_log_$BUILD_ID; echo ${PIPESTATUS[0]} > $WORKSPACE/result_$BUILD_ID
