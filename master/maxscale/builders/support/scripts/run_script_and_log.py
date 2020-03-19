#!/usr/bin/env python3

import argparse
import os
import logging
import sys
import subprocess


def main():
    logging.basicConfig(level=logging.INFO)
    arguments = parseArguments()
    scriptPath = os.path.join("maxscale-system-test/mdbci/", arguments.script_name)
    if not os.path.exists(scriptPath):
        logging.error("The script '%s' doest not exist. Unable to execute it", scriptPath)
        sys.exit(1)
    runScript(scriptPath, arguments.log_file, arguments.result_file)


def parseArguments():
    logging.info("Parsing command line arguments")
    parser = argparse.ArgumentParser(description="Tool to run script and log it's results into the file")
    parser.add_argument("--script_name", help="Name of the script to run", required=True)
    parser.add_argument("--log_file", help="Location of the log file to put data into", required=True)
    parser.add_argument("--result_file", help="Location of the file with test results", required=True)
    return parser.parse_args()


def runScript(scriptPath, buildLogFile, resultFile):
    logging.info("Executing script '%s'", scriptPath)
    logFile = open(buildLogFile, "w")
    process = subprocess.Popen([scriptPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for byteLine in process.stdout:
        line = byteLine.decode("utf-8", "replace")
        sys.stdout.write(line)
        sys.stdout.flush()
        logFile.write(line)
    process.wait()
    logFile.close()

    testLogFile = open(resultFile, "w")
    testLogFile.write(str(process.returncode))
    testLogFile.close()
    sys.exit(process.returncode)


if __name__ == '__main__':
    main()
