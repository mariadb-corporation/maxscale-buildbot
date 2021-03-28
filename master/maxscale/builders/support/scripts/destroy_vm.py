#!/usr/bin/env python3
# Script to destroy MDBCI configurations and respective VMs

from argparse import ArgumentParser
import os
import pathlib
import shutil
import sys

sys.path.append(pathlib.Path(__file__).parent.absolute())
import common


def main():
    arguments = parse_arguments()
    common.setupMdbciEnvironment()
    if arguments.destroy_all:
        result = common.runMdbci('destroy', '--all', os.path.expanduser(arguments.config_dir), '--force')
        shutil.rmtree(arguments.config_dir, ignore_errors=True)
    else:
        result = common.runMdbci('destroy', arguments.config_name, '--force')
    sys.exit(result)


def parse_arguments():
    parser = ArgumentParser(description="Tool to destroy VM or a set of VMs")
    parser.add_argument("--destroy-all", dest="destroy_all", help="Whether to destroy all machines in the directory",
                        default=False, action='store_true')
    parser.add_argument("--configuration-dir", dest="config_dir", help="Directory of all MDBCI configurations",
                        default="~/build_vms")
    parser.add_argument("--configuration-name", dest="config_name", help="Name of MDBCI configuration",
                        default="build_vm")
    return parser.parse_args()


if __name__ == "__main__":
    main()
