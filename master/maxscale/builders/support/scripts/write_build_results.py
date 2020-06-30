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
RUN_ID_OPTION = '--run-id'

# Db parameters
DEFAULT_FILE = '{}/build_parser_db_password'.format(os.environ['HOME'])
DB_NAME = 'test_results_db'

# parse_ctest_log.rb keys definition
TEST_NAME = 'test_name'
TEST_TIME = 'test_time'
TEST_SUCCESS = 'test_success'
PASSED = 'Passed'

ERROR = 'Error'

DB_WRITE_ERROR = 'DB_WRITE_ERROR'


options = argparse.ArgumentParser(description="write_build_results usage:")
options.add_argument(INPUT_FILE_OPTION, help="parse_ctest_log.rb result json file")
options.add_argument("-r", RUN_ID_OPTION, help="id of main task (run id)")
options.add_argument("-e", ENV_FILE_OPTION,
                     help="ENVIRONMENT VARIABLES FILE, WHERE POSSIBLE DB_WRITING_ERROR CAN BE REPORTED")


class BuildResultsWriter:

    def __init__(self, runId):
        self.client = None
        self.parsedContent = None
        self.runId = runId

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

    def findTestCase(self, name):
        cursor = self.client.cursor(dictionary=True)
        query = """
                SELECT id FROM test_cases
                WHERE name=%s
                """
        cursor.execute(query, (name,))
        test_case = cursor.fetchone()
        cursor.close()
        if test_case is None:
            return None
        else:
            return test_case["id"]

    def writeTestCasesTable(self, name):
        test_case_id = self.findTestCase(name)
        if test_case_id:
            return test_case_id
        cursor = self.client.cursor()
        query = "INSERT INTO test_cases (name) VALUES (%s)"
        values = (name,)
        cursor.execute(query, values)
        id = cursor.lastrowid
        self.client.commit()
        cursor.close()
        print("Performed insert (test_case, id = {}: {}".format(id, query % values))
        return id

    def findTargetBuild(self, runId):
        cursor = self.client.cursor(dictionary=True)
        query = """
                SELECT id FROM target_builds
                WHERE run_id=%s
                """
        cursor.execute(query, (runId,))
        target_build = cursor.fetchone()
        cursor.close()
        if target_build is None:
            return None
        else:
            return target_build["id"]

    def writeTargetBuildsTable(self, runId, startTime, target, box, product, mariadbVersion,
                          testCodeCommitId, maxscaleCommitId, cmakeFlags, maxscaleSource):
        target_build_id = self.findTargetBuild(runId)
        if target_build_id:
            return target_build_id
        cursor = self.client.cursor()
        query = ("INSERT INTO target_builds (run_id, "
                 "start_time, target, box, product, mariadb_version, "
                 "test_code_commit_id, maxscale_commit_id, "
                 "cmake_flags, maxscale_source) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        values = (runId, startTime, target, box, product, mariadbVersion,
                  testCodeCommitId, maxscaleCommitId,
                  cmakeFlags, maxscaleSource)
        cursor.execute(query, values)
        id = cursor.lastrowid
        self.client.commit()
        cursor.close()
        print("Performed insert (target_build, id = {}: {}".format(id, query % values))
        return id

    def writeTargetBuildStartTime(self, targetBuildId):
        query = f"""
        UPDATE target_builds
        SET start_time = (
                SELECT MIN(start_time) AS start_time
                FROM test_run
                WHERE target_build_id = %(id)s
            )
        WHERE id = %(id)s
        """
        cursor = self.client.cursor()
        cursor.execute(query, {"id": targetBuildId})
        self.client.commit()
        cursor.close()

    def writeTestRunTable(self, targetBuildId, jenkinsId, startTime, targat, box, product, mariadbVersion,
                          testCodeCommitId, maxscaleCommitId, jobName,
                          cmakeFlags, maxscaleSource, logsDir):
        cursor = self.client.cursor()
        query = ("INSERT INTO test_run (jenkins_id, "
                 "start_time, target, box, product, mariadb_version, "
                 "test_code_commit_id, maxscale_commit_id, job_name, "
                 "cmake_flags, maxscale_source, logs_dir, target_build_id) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        values = (jenkinsId, startTime, targat, box, product, mariadbVersion,
                  testCodeCommitId, maxscaleCommitId, jobName,
                  cmakeFlags, maxscaleSource, logsDir, targetBuildId)
        cursor.execute(query, values)
        id = cursor.lastrowid
        self.client.commit()
        cursor.close()
        print("Performed insert (test_run, id = {}: {}".format(id, query % values))
        return id

    def writeResultsTable(self, id, test, result, testTime, coreDumpPath, leakSummary, targetBuildId, testCaseId):
        cursor = self.client.cursor()
        query = ("INSERT INTO results (id, test, result, test_time, core_dump_path, "
                 "leak_summary, target_build_id, test_case_id) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        values = (id, test, result, testTime, coreDumpPath, leakSummary, targetBuildId, testCaseId)
        cursor.execute(query, values)
        self.client.commit()
        cursor.close()
        print("Performed insert (results): {}".format(query % values))

    def findCoreDumpPath(self, runTestDir, testName):
        coreDumpPathRegex = re.compile(br".*\/run_test[^\/.+]+(\/.+)")
        dir = "{}/LOGS/{}/LOGS/{}".format(os.environ['HOME'], runTestDir, testName)
        if not os.path.isdir(dir):
            return ""
        result = subprocess.check_output(["find {} | grep core | sed -e 's|/[^/]*$|/*|g'".format(dir)],
                                         shell=True)
        if not result or not coreDumpPathRegex.match(result):
            return ""
        return coreDumpPathRegex.match(result).group(0)

    def writeBuildResultsToDb(self, results):
        tests = []
        if results.get("tests"):
            for test in results["tests"]:
                tests.append({
                    TEST_NAME: test[TEST_NAME],
                    TEST_SUCCESS: test[TEST_SUCCESS],
                    TEST_TIME: test[TEST_TIME]
                })
        testsLeakSummary = results["leak_summary"]

        targetBuildId = self.writeTargetBuildsTable(self.runId, None, *(results[key] for key in (
            "target", "box", "product", "version", "maxscale_system_test_commit",
            "maxscale_commit", "cmake_flags", "maxscale_source"
        )))
        id = self.writeTestRunTable(targetBuildId, *(results[key] for key in (
            "job_build_number", "timestamp", "target", "box",
            "product", "version", "maxscale_system_test_commit",
            "maxscale_commit", "job_name", "cmake_flags", "maxscale_source",
            "logs_dir"
        )))
        self.writeTargetBuildStartTime(targetBuildId)

        if not results.get(ERROR):
            for test in tests:
                print("Preparing to write test={} into results".format(test))
                name = test[TEST_NAME]
                result = int(test[TEST_SUCCESS] != PASSED)
                testTime = test[TEST_TIME]
                coreDumpPath = self.findCoreDumpPath(results["logs_dir"], name)
                if (name in testsLeakSummary) and (testsLeakSummary[name]):
                    leakSummary = ";\n".join(testsLeakSummary[name])
                else:
                    leakSummary = None
                testCaseId = self.writeTestCasesTable(name)
                self.writeResultsTable(id, name, result, testTime, coreDumpPath, leakSummary, targetBuildId, testCaseId)


def main(args=None):
    args = options.parse_args(args=args)
    try:
        writer = BuildResultsWriter(args.run_id)
        writer.writeResultsFromInputFile(args.file)
    except Exception as e:
        print(e)
        if args.env_file:
            with open(args.env_file, "w") as file:
                file.write("{} {}".format(DB_WRITE_ERROR, e.__cause__))
        sys.exit(1)


if os.path.samefile(__file__, sys.argv[0]):
    print("Starting ./write_build_results.py")
    main()
    print("./write_build_results.py finished")
