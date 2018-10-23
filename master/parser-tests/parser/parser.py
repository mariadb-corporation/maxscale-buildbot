#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys

LOG_FILE_OPTION = 'log_file'
OUTPUT_PATH_OPTION = '--output-path'
ONLY_FAILED_OPTION = '--only-failed'
HUMAN_READABLE_OPTION = '--human-readable'
USE_RUBY_PARSER_OPTION = '--use-ruby'
FIND_COREDUMPS_OPTION = "--find-coredumps"
WRITE_RESULTS_TO_DATABASE_OPTION = "--write-to-database"
HELP_OPTION = '--help'

options = argparse.ArgumentParser(description="CTest parser usage:")
options.add_argument(LOG_FILE_OPTION, help="CTEST LOG FILE PATH")
options.add_argument("-f", ONLY_FAILED_OPTION, action="store_true", help="PARSE ONLY FAILED TESTS")
options.add_argument("-r", HUMAN_READABLE_OPTION, action="store_true", help="HUMAN READABLE OUTPUT")
options.add_argument("-o", OUTPUT_PATH_OPTION, metavar="output_path", help="OUTPUT DIRECTORY PATH")
options.add_argument("-u", USE_RUBY_PARSER_OPTION, action="store_true", help="USE OLD RUBY PARSER")
options.add_argument("-c", FIND_COREDUMPS_OPTION, choices=["url", "files"], help="FIND AND STORE COREDUMPS")
options.add_argument("-w", WRITE_RESULTS_TO_DATABASE_OPTION, action="store_true", help="WRITE TEST RESULTS TO DATABASE")


parserRoot = os.path.dirname(os.path.abspath(__file__))


def parseCtestRuby(opts, path, outputDir):
    command = [
        "{}/ruby-scripts/parse_ctest_log.rb".format(parserRoot),
        "-l", opts.log_file,
        "-o", "{}/{}/ruby/results".format(path, outputDir),
        "-j", "{}/{}/ruby/json".format(path, outputDir),
        "-s", "{}/{}/ruby/ctest_sublogs".format(path, outputDir)
    ]
    if opts.human_readable:
        command.append("-r")
    if opts.only_failed:
        command.append("-f")
    return subprocess.check_output(command)


def parseCtestPython(opts, path, outputDir):
    command = [
        "{}/python-scripts/parse_ctest_log.py".format(parserRoot),
        opts.log_file,
        "-o", "{}/{}/python/results".format(path, outputDir),
        "-j", "{}/{}/python/json".format(path, outputDir),
        "-s", "{}/{}/python/ctest_sublogs".format(path, outputDir)
    ]
    if opts.human_readable:
        command.append("-r")
    if opts.only_failed:
        command.append("-f")
    return subprocess.check_output(command)


def storeCoredumpsRuby(opts, buildId, path, outputDir):
    command = [
        "{}/ruby-scripts/coredump_finder.sh".format(parserRoot),
        buildId,
        opts.find_coredumps
    ]
    coredumps = subprocess.check_output(command)
    writeCoredumpsToFile("{}/{}/ruby/coredump".format(path, outputDir), coredumps)


def storeCoredumpsPython(opts, buildId, path, outputDir):
    command = [
        "{}/python-scripts/coredump_finder.py".format(parserRoot),
        buildId,
        opts.find_coredumps
    ]
    coredumps = subprocess.check_output(command)
    writeCoredumpsToFile("{}/{}/python/coredump".format(path, outputDir), coredumps)


def getLogsDir(output):
    return re.search(b'(Logs dir: |"logs_dir": ")(\w+-\d+)', output).group(2)


def writeCoredumpsToFile(path, coredumps):
    file = open(path, "w")
    file.write("COREDUMPS \\\n")
    file.writelines(coredumps)
    file.close()


def writeToDatabaseRuby(opts, path):
    command = [
        "{}/ruby-scripts/write_build_results.rb".format(parserRoot),
        "{}/ruby/json".format(path)
    ]
    return subprocess.check_output(command)


def writeToDatabasePython(opts, path):
    command = [
        "{}/python-scripts/write_build_results.py".format(parserRoot),
        "{}/python/json".format(path)
    ]
    return subprocess.check_output(command)


def main(args=None):
    opts = options.parse_args(args=args)
    (path, file) = os.path.split(os.path.abspath(opts.log_file))
    if opts.output_path:
        path = opts.output_path

    if opts.use_ruby:
        result = parseCtestRuby(opts, path, file)
        if opts.find_coredumps:
            storeCoredumpsRuby(opts, getLogsDir(result), path, file)
        if opts.write_to_database:
            writeToDatabaseRuby(opts, path)
    else:
        result = parseCtestPython(opts, path, file)
        if opts.find_coredumps:
            storeCoredumpsPython(opts, getLogsDir(result), path, file)
        if opts.write_to_database:
            writeToDatabasePython(opts, path)


if os.path.samefile(__file__, sys.argv[0]):
    main()
