#!/usr/bin/env python3

import sys
import os.path
import argparse
import getpass
sys.path.append(os.path.abspath("{}/../../master/".format(__file__)))
import maxscale.config.workers as workers


def parse_arguments():
    parser = argparse.ArgumentParser(description="A tool to install, restart the BuildBot worker instances.")
    parser.add_argument("action", help="Action to perform, install for example.")
    parser.add_argument("--host", help="Host to manage.")
    parser.add_argument("--user", help="User to use during the SSH connection to host.", default=getpass.getuser())
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    print(arguments)


if __name__ == "__main__":
    main()
