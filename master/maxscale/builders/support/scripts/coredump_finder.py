#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess

options = argparse.ArgumentParser(description="Core dump finder")
options.add_argument("build_id", help="Id of the build (<build_name>_<build_number>)")
options.add_argument("output_format", help="Output format (url|files)", choices=["url", "files"])


def main(args=None):
    args = options.parse_args(args=args)
    HOME = os.environ["HOME"]
    LOG_SERVER = 'http://max-tst-01.mariadb.com'
    logsPath = "{}/LOGS".format(HOME)
    buildPath = "{}/{}".format(logsPath, args.build_id)

    if not os.path.isdir(buildPath):
        print("Directory {} does not exist, exiting.".format(buildPath))
        sys.exit(1)

    if args.output_format == "url":
        def coredumpPath(dirpath, filename):
            return "{}/{}".format(dirpath.rstrip('/'), filename).replace(HOME, LOG_SERVER)
    else:
        def coredumpPath(dirpath, filename):
            return "{}/*".format(dirpath.rstrip('/')).replace('{}/LOGS'.format(HOME), '*')

    for dirpath, dirnames, filenames in os.walk(buildPath):
        for name in filenames:
            if "core" in name:
                print(coredumpPath(dirpath, name))


if os.path.samefile(__file__, sys.argv[0]):
    main()
