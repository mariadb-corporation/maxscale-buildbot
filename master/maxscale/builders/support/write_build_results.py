#!/usr/bin/env python3

import os
import re
import sys
import subprocess
import argparse
import mysql


# Command line options
INPUT_FILE_OPTION = '--file'
ENV_FILE_OPTION = '--env-file'
HELP_OPTION = '--help'

# Db parameters
DEFAULT_FILE = '/home/vagrant/build_parser_db_password'
DB_NAME = 'test_results_db'

# parse_ctest_log.rb keys definition
TEST_NAME = 'test_name'
TEST_TIME = 'test_time'
TEST_SUCCESS = 'test_success'
FAILED = 'Failed'

ERROR = 'Error'

DB_WRITE_ERROR = 'DB_WRITE_ERROR'


options = argparse.ArgumentParser(description="write_build_results usage:")
options.add_argument(INPUT_FILE_OPTION, help="parse_ctest_log.rb result json file")
options.add_argument("-e", ENV_FILE_OPTION,
                     help="ENVIRONMENT VARIABLES FILE, WHERE POSSIBLE DB_WRITING_ERROR CAN BE REPORTED")


class BuildResultsWriter:

    def __init__(self):
        self.client = None
        self.parsedContent = None

    def writeResultsFromInputFile(self, inputFilePath):
        pass


def main():
    args = options.parse_args()
    try:
        writer = BuildResultsWriter()
        writer.writeResultsFromInputFile(args.file)
    except Exception as e:
        print(e.__cause__)
        print(e.__traceback__)
        if args.env_file:
            with open(args.env_file, "rw") as file:
                file.write("{} {}".format(DB_WRITE_ERROR, e.__cause__))


if os.path.samefile(__file__, sys.argv[0]):
    print("Starting ./write_build_results.py")
    main()
    print("./write_build_results.py finished")
