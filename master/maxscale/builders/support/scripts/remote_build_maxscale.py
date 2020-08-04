#!/usr/bin/env python3

import os
import argparse
import logging
import subprocess
import sys
import shutil


def parseArguments():
    logging.info("Parsing command line arguments")
    parser = argparse.ArgumentParser(description="Tool for running the script for creating a full repository")
    parser.add_argument("--repository", help="Name of the MaxScale repository", required=True)
    return parser.parse_args()


def main():
    arguments = parseArguments()
    if not os.path.exists("BUILD/mdbci"):
        os.mkdir("default-maxscale-branch")
        os.chdir("default-maxscale-branch")
        subprocess.run(["git", "clone", arguments.repository])
        os.chdir("..")
    if not os.path.isdir("BUILD"):
        shutil.copytree("default-maxscale-branch/MaxScale/BUILD", ".")
    if not os.path.isdir("BUILD/mdbci"):
        shutil.copytree("default-maxscale-branch/MaxScale/BUILD/mdbci", "BUILD/")
    results = subprocess.run(["BUILD/mdbci/create_full_repo.sh"])
    sys.exit(results.returncode)


if __name__ == '__main__':
    main()
