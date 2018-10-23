#!/usr/bin/env python3

import json
import os
import re
import sys
import subprocess
import argparse
import mysql.connector
from configparser import ConfigParser


# Command line options
INPUT_FILE_OPTION = 'file'
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
        self.parseInputFile(inputFilePath)
        self.connectMdb(DEFAULT_FILE, DB_NAME)
        self.writeBuildResultsToDb(self.parsedContent)
        self.client.close()

    def parseInputFile(self, inputFilePath):
        with open(inputFilePath, "r") as file:
            self.parsedContent = json.load(file)

    def connectMdb(self, defaultFile, dbName):
        self.client = mysql.connector.connect(database=dbName, **self.readDatabaseConfiguration(defaultFile))
        print("Successfully connected to database {} using configuration {}"
              .format(dbName, defaultFile))

    def readDatabaseConfiguration(self, filename, section="client"):
        config = ConfigParser()
        config.read(filename)
        db = {}
        if config.has_section(section):
            for item in config.items(section):
                db[item[0]] = item[1]
        else:
            raise Exception("{} not found in the {} file".format(section, filename))
        return db

    def writeTestRunTable(self, jenkinsId, startTime, targat, box, product, mariadbVersion,
                          testCodeCommitId, maxscaleCommitId, jobName,
                          cmakeFlags, maxscaleSource, logsDir):
        cursor = self.client.cursor()
        query = ("INSERT INTO test_run (jenkins_id, "
                 "start_time, target, box, product, mariadb_version, "
                 "test_code_commit_id, maxscale_commit_id, job_name, "
                 "cmake_flags, maxscale_source, logs_dir) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        values = (jenkinsId, startTime, targat, box, product, mariadbVersion,
                  testCodeCommitId, maxscaleCommitId, jobName,
                  cmakeFlags, maxscaleSource, logsDir)
        cursor.execute(query, values)
        id = cursor.lastrowid
        self.client.commit()
        cursor.close()
        print("Performed insert (test_run, id = {}: {}".format(id, query % values))
        return id

    def writeResultsTable(self, id, test, result, testTime, coreDumpPath):
        cursor = self.client.cursor()
        query = ("INSERT INTO results (id, test, result, test_time, core_dump_path) "
                 "VALUES (%s, %s, %s, %s, %s)")
        values = (id, test, result, testTime, coreDumpPath)
        cursor.execute(query, values)
        self.client.commit()
        cursor.close()
        print("Performed insert (results): {}".format(query % values))

    def findCoreDumpPath(self, runTestDir, testName):
        coreDumpPathRegex = re.compile(r".*\/run_test[^\/.+]+(\/.+)")
        dir = "/home/vagrant/LOGS/{}/LOGS/{}".format(runTestDir, testName)
        if not os.path.isdir(dir):
            return ""
        result = subprocess.run(["find {} | grep core | sed -e 's|/[^/]*$|/*|g".format(dir)],
                                stdout=subprocess.PIPE).stdout
        if not result or not coreDumpPathRegex.match(result):
            return ""
        return coreDumpPathRegex.match(result)[0]

    def writeBuildResultsToDb(self, results):
        tests = []
        if results.get("tests"):
            for test in results["tests"]:
                tests.append({
                    TEST_NAME: test[TEST_NAME],
                    TEST_SUCCESS: test[TEST_SUCCESS],
                    TEST_TIME: test[TEST_TIME]
                })

        id = self.writeTestRunTable(*(results[key] for key in (
            "job_build_number", "timestamp", "target", "box",
            "product", "version", "maxscale_system_test_commit",
            "maxscale_commit", "job_name", "cmake_flags", "maxscale_source",
            "logs_dir"
        )))

        if not results.get(ERROR):
            for test in tests:
                print("Preparing to write test={} into results")
                name = test[TEST_NAME]
                result = int(test[TEST_SUCCESS] == FAILED)
                testTime = test[TEST_TIME]
                coreDumpPath = self.findCoreDumpPath(results["logs_dir"], name)
                self.writeResultsTable(id, name, result, testTime, coreDumpPath)


def main(args=None):
    args = options.parse_args(args=args)
    try:
        writer = BuildResultsWriter()
        writer.writeResultsFromInputFile(args.file)
    except Exception as e:
        print(e)
        if args.env_file:
            with open(args.env_file, "w") as file:
                file.write("{} {}".format(DB_WRITE_ERROR, e.__cause__))


if os.path.samefile(__file__, sys.argv[0]):
    print("Starting ./write_build_results.py")
    main()
    print("./write_build_results.py finished")
