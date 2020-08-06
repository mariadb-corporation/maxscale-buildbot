#!/usr/bin/env python3

import os
import subprocess
import sys
import argparse


def parseArguments():
    parser = argparse.ArgumentParser(description="Tool for running the performance test")
    parser.add_argument("--build_dir", help="Format for recording results. Build directory", required=True)
    parser.add_argument("--build_number", help="Format for recording results. Build number", required=True)
    parser.add_argument("--network_config_path", help="Path to the network config. Args for the --server-config flag", required=True)
    parser.add_argument("--version", help="MariaDB version. Args for --mariadb-version flag", required=True)
    parser.add_argument("--perf_cnf_template", help="Path to the MaxScale config. Args for the --maxscale-config flag", required=True)
    parser.add_argument("--target", help="MaxScale version. Args for --mariadb-version flag", required=True)
    return parser.parse_args()


def main():
    arguments = parseArguments()
    os.chdir('{}/maxscale-performance-test/'.format(os.environ['HOME']))
    if 'COMP_WORDBREAKS' in os.environ:
        del os.environ['COMP_WORDBREAKS']

    logFile = open('{}/results_{}'.format(arguments.build_dir, arguments.build_number), 'w')
    process = subprocess.Popen(['./bin/performance_test', '-v',
                                '--server-config', '{}/{}'.format(os.environ['HOME'], arguments.network_config_path),
                                '--remote-test-app',
                                '{}/.config/performance_test/run_sysbench.sh'.format(os.environ['HOME']),
                                '--db-server-2-config', 'slave-config.sql.erb',
                                '--db-server-3-config', 'slave-config.sql.erb',
                                '--db-server-4-config', 'slave-config.sql.erb',
                                '--mariadb-version', arguments.version,
                                '--maxscale-config', arguments.perf_cnf_template,
                                '--maxscale-version', arguments.target,
                                '--keep-servers', 'true'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for byteLine in process.stdout:
        line = byteLine.decode("utf-8", "replace")
        sys.stdout.write(line)
        logFile.write(line)
    process.wait()
    logFile.close()
    sys.exit(process.returncode)


if __name__ == '__main__':
    main()
