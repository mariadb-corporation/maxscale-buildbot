#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess

options = argparse.ArgumentParser(description="Core dump finder")
options.add_argument("build_id", help="Id of the build (<build_name>_<build_number>)")
options.add_argument("output_format", help="(url|files)", choices=["url", "files"])

args = options.parse_args()
HOME = os.environ["HOME"]
logsPath = "{}/LOGS".format(HOME)
buildPath = "{}/{}".format(logsPath, args.build_id)

if not os.path.isdir(buildPath):
    print("Directory {} does not exist, exiting.".format(buildPath))
    sys.exit(1)

if args.output_format == "url":
    sys.exit(subprocess.run(['find {} | grep core | sed -e "s|{}/|http://max-tst-01.mariadb.com/|"'
                            .format(buildPath, HOME)], shell=True).returncode)

pwd = os.getcwd()
os.chdir(buildPath)
subprocess.run([r"find ./ | grep core | sed -e 's|/[^/]*$|/*|g'"], shell=True)
os.chdir(pwd)
sys.exit(0)
