#!/usr/bin/env python3

import json
import os
import re
import sys
import subprocess
import argparse

LOG_FILE_OPTION = 'log_file'
OUTPUT_LOG_FILE_OPTION = '--output-log-file'
OUTPUT_LOG_JSON_FILE_OPTION = '--output-log-json-file'
ONLY_FAILED_OPTION = '--only-failed'
HUMAN_READABLE_OPTION = '--human-readable'
CTEST_SUBLOGS_PATH = '--ctest-sublogs-path'
HELP_OPTION = '--help'

TEST_INDEX_NUMBER = 'test_index_number'
TEST_NUMBER = 'test_number'
TEST_NAME = 'test_name'
TEST_SUCCESS = 'test_success'
TEST_TIME = 'test_time'
TESTS = 'tests'
TESTS_COUNT = 'tests_count'
FAILED_TESTS_COUNT = 'failed_tests_count'

RUN_TEST_BUILD_ENV_VARS_TO_HR = {
    'BUILD_NUMBER': 'Job build number',
    'JOB_NAME': 'Job name',
    'BUILD_TIMESTAMP': 'Timestamp',
    'name': 'Test run name',
    'target': 'Target',
    'box': 'Box',
    'product': 'Product',
    'version': 'Version'
}

RUN_TEST_BUILD_ENV_VARS_TO_MR = {
    'BUILD_NUMBER': 'job_build_number',
    'JOB_NAME': 'job_name',
    'BUILD_TIMESTAMP': 'timestamp',
    'name': 'test_run_name',
    'target': 'target',
    'box': 'box',
    'product': 'product',
    'version': 'version'
}

FIRST_LINES_CTEST_TO_SKIP = [
    'Constructing a list of tests',
    'Done constructing a list of tests',
    'Checking test dependency graph...',
    'Checking test dependency graph end'
]

WORKSPACE = 'WORKSPACE'

FAILED = 'Failed'
PASSED = 'Passed'

NOT_FOUND = 'NOT FOUND'

BUILD_LOG_PARSING_RESULT = 'BUILD_LOG_PARSING_RESULT'

ERROR = 'Error'
CTEST_NOT_EXECUTED_ERROR = 'CTest has never executed'
CTEST_SUMMARY_NOTE_FOUND = 'CTest summary has not found'

CTEST_ARGUMENTS_HR = 'CTest arguments'
CTEST_ARGUMENTS_MR = 'ctest_arguments'

MAXSCALE_COMMIT_HR = "MaxScale commit"
MAXSCALE_COMMIT_MR = "maxscale_commit"

MAXSCALE_SOURCE_HR = "MaxScale source"
MAXSCALE_SOURCE_MR = "maxscale_source"

CMAKE_FLAGS_HR = "CMake flags"
CMAKE_FLAGS_MR = "cmake_flags"

LOGS_DIR_HR = "Logs dir"
LOGS_DIR_MR = "logs_dir"

MAXSCALE_SYSTEM_TEST_COMMIT_HR = "MaxScale system test commit"
MAXSCALE_SYSTEM_TEST_COMMIT_MR = "maxscale_system_test_commit"

MAXSCALE_FULL = "Maxscale full version"

NEW_LINE_JENKINS_FORMAT = " \\n\\\n"


options = argparse.ArgumentParser(description="CTest parser usage:")
options.add_argument(LOG_FILE_OPTION, help="CTEST LOG FILE PATH")
options.add_argument("-f", ONLY_FAILED_OPTION, action="store_true", help="PARSE ONLY FAILED TESTS")
options.add_argument("-r", HUMAN_READABLE_OPTION, action="store_true", help="HUMAN READABLE OUTPUT")
options.add_argument("-o", OUTPUT_LOG_FILE_OPTION, metavar="file_path",
                     help="CTEST PARSER OUTPUT LOG FILE HUMAN READABLE "
                          "FOR JENKINS (environmental variable format)")
options.add_argument("-j", OUTPUT_LOG_JSON_FILE_OPTION, metavar="json_file_path",
                     help="CTEST PARSER OUTPUT LOG JSON FILE (there will be "
                          "saved all test results - passed and failed)")
options.add_argument("-s", CTEST_SUBLOGS_PATH, help="Path to ctest sublogs")


class CTestParser:

    def __init__(self, args):
        self.args = args
        self.ctestExecuted = False
        self.ctestSummary = None
        self.maxscaleCommit = None
        self.cmakeFlags = None
        self.maxscaleSource = None
        self.logsDir = None
        self.allCtestIndexes = []
        self.failedCtestIndexes = []
        self.allCtestArguments = None
        self.failedCtestArguments = None
        self.allCtestInfo = []
        self.failedCtestInfo = []
        self.failCtestCounter = 0
        self.maxscaleEntity = []

    def parseCtestLog(self):
        ctestFirstLineRegex = re.compile("Constructing a list of tests")
        ctestLastLineRegex = re.compile("tests passed,.+tests failed out of (.+)")
        maxscaleCommitRegex = re.compile(r"MaxScale\s+.*\d+\.*\d*\.*\d*\s+-\s+(.+)")
        cmakeFlagsRegex = re.compile(r"CMake flags:\s+(.+)")
        maxscaleSourceRegex = re.compile(r"Source:\s+(.+)")
        logsFirRegex = re.compile(r"^Logs go to \/home\/vagrant\/LOGS\/(.+)$")
        maxscaleVersionStartRegex = re.compile(".*Maxscale_full_version_start:.*")
        maxscaleVersionEndRegex = re.compile(".*Maxscale_full_version_end.*")
        maxscaleVersionStartFound = False
        maxscaleVersionEndFound = False

        with open(self.args.log_file, encoding="UTF-8") as file:
            for line in file:
                if maxscaleVersionEndRegex.search(line):
                    maxscaleVersionEndFound = True
                if maxscaleVersionStartFound and not maxscaleVersionEndFound and line.strip():
                    self.maxscaleEntity.append(line.strip())
                if maxscaleVersionStartRegex.search(line):
                    maxscaleVersionStartFound = True
                if maxscaleCommitRegex.search(line) and not self.maxscaleCommit:
                    self.maxscaleCommit = maxscaleCommitRegex.search(line).group(0)
                if cmakeFlagsRegex.search(line) and not self.cmakeFlags:
                    self.cmakeFlags = cmakeFlagsRegex.search(line).group(0).strip()
                if maxscaleSourceRegex.search(line) and not self.maxscaleSource:
                    self.maxscaleSource = maxscaleSourceRegex.search(line).group(0).strip()
                if logsFirRegex.search(line) and not self.logsDir:
                    self.logsDir = logsFirRegex.search(line).group(0).strip()
                if ctestFirstLineRegex.search(line):
                    self.ctestExecuted = True
                    break

            if self.ctestExecuted:
                ctestLog = []
                testQuantity = 0
                for line in file:
                    if ctestLastLineRegex.search(line):
                        self.ctestSummary = line.strip()
                        testQuantity = ctestLastLineRegex.search(line).group(0)
                        break
                    ctestLog.append(line)

                self.findTestsInfo(ctestLog)
                self.allCtestInfo.update({TESTS_COUNT: testQuantity})
                self.failedCtestInfo.update({TESTS_COUNT: testQuantity})
            else:
                self.ctestSummary = CTEST_SUMMARY_NOTE_FOUND
                self.allCtestInfo = {TESTS_COUNT: NOT_FOUND, FAILED_TESTS_COUNT: NOT_FOUND, TESTS: []}
                self.failedCtestInfo = {TESTS_COUNT: NOT_FOUND, FAILED_TESTS_COUNT: NOT_FOUND, TESTS: []}

    def findTestsInfo(self, ctestLog):
        if self.args.ctest_sublogs_path:
            os.makedirs(self.args.ctest_sublogs_path, exist_ok=True)
        ctestSublog = []
        for line in ctestLog:
            testEndRegex = re.compile(r"(\d+)\/(\d+)\s+Test\s+#(\d+):[\s]+([^\s]+)\s+[\.\*]+([^\d]+)([\d\.]+)")
            if line not in FIRST_LINES_CTEST_TO_SKIP:
                ctestSublog.append(line)
            if testEndRegex.search(line):
                testIndexNumber = testEndRegex.search(line).group(0)
                testSuccess = testEndRegex.search(line).group(4).strip()
                testName = testEndRegex.search(line).group(3)
                if self.args.ctest_sublogs_path:
                    os.makedirs("{}/{}".format(self.args.ctest_sublogs_path, testName), exist_ok=True)
                    with open("{}/{}/ctest_sublog".format(self.args.ctest_sublogs_path, testName), "w") as file:
                        file.writelines(ctestSublog)
                ctestSublog = []
                testNumber = testEndRegex.search(line).group(2)
                testTime = testEndRegex.search(line).group(5)
                self.allCtestIndexes.append(testNumber)
                self.allCtestInfo.append({
                    TEST_INDEX_NUMBER: testIndexNumber,
                    TEST_NUMBER: testNumber,
                    TEST_NAME: testName,
                    TEST_SUCCESS: testSuccess,
                    TEST_TIME: testTime
                })
                if testSuccess != PASSED:
                    self.failCtestCounter += 1
                    self.failedCtestIndexes.append(testNumber)
                    self.failedCtestInfo.append({
                        TEST_INDEX_NUMBER: testIndexNumber,
                        TEST_NUMBER: testNumber,
                        TEST_NAME: testName,
                        TEST_SUCCESS: testSuccess,
                        TEST_TIME: testTime
                    })
        self.allCtestInfo = {FAILED_TESTS_COUNT: self.failCtestCounter, TESTS: self.allCtestInfo}
        self.failedCtestInfo = {FAILED_TESTS_COUNT: self.failCtestCounter, TESTS: self.failedCtestInfo}

    def generateCtestArguments(self):
        if not self.ctestExecuted:
            return NOT_FOUND
        ctestArguments = []
        testIndexesArray = self.failedCtestIndexes if self.args.only_failed else self.allCtestIndexes
        sortedTestIndexesArray = sorted(testIndexesArray, key=lambda item: item)
        if not sortedTestIndexesArray:
            return NOT_FOUND
        for testIndex in sortedTestIndexesArray:
            if testIndex == sortedTestIndexesArray[0]:
                ctestArguments.extend([testIndex, testIndex])
                if len(sortedTestIndexesArray) > 1:
                    ctestArguments.append("1")
            else:
                ctestArguments.append(testIndex)
        return ",".join(ctestArguments)

    def getTestCodeCommit(self):
        if not os.environ.get(WORKSPACE):
            return NOT_FOUND
        currentDirectory = os.getcwd()
        os.chdir(os.environ.get(WORKSPACE))
        gitLog = subprocess.Popen("git log -1", stdout=subprocess.PIPE).stdout
        os.chdir(currentDirectory)
        if not gitLog:
            return NOT_FOUND
        commitRegex = re.compile(r"commit\s+(.+)")
        if commitRegex.search(gitLog.readlines()):
            return commitRegex.search(gitLog.readlines()[0]).group(0)
        return NOT_FOUND

    def generateRunTestBuildParametersHr(self):
        buildParams = []
        for (key, value) in RUN_TEST_BUILD_ENV_VARS_TO_HR.items():
            envValue = os.environ.get(key) or NOT_FOUND
            buildParams.append("{}: {}".format(value, envValue))
        return buildParams

    def generateRunTestBuildParametersMr(self):
        buildParams = {}
        for (key, value) in RUN_TEST_BUILD_ENV_VARS_TO_MR.items():
            envValue = os.environ.get(key) or NOT_FOUND
            buildParams[value] = envValue
        return buildParams

    def generateHrResult(self, parsedCtestData):
        hrTests = []
        hrTests.append(self.ctestSummary)
        for test in parsedCtestData[TESTS]:
            hrTests.append("{} - {} ({})".format(test[TEST_NUMBER], test[TEST_NAME], test[TEST_SUCCESS]))
        hrTests.extend(["", "{}: {}".format(CTEST_ARGUMENTS_HR, self.generateCtestArguments()), ""])
        maxscaleCommit = self.maxscaleCommit or NOT_FOUND
        maxscaleSource = self.maxscaleSource or NOT_FOUND
        cmakeFlags = self.cmakeFlags or NOT_FOUND
        logsDir = self.logsDir or NOT_FOUND
        hrTests.append("{}: {}".format(MAXSCALE_COMMIT_HR, maxscaleCommit))
        hrTests.append("{}: {}".format(MAXSCALE_SOURCE_MR, maxscaleSource))
        hrTests.append("{}: {}".format(LOGS_DIR_HR, logsDir))
        hrTests.append("{}: {}".format(CMAKE_FLAGS_HR, cmakeFlags))
        hrTests.append("{}: {}".format(MAXSCALE_SYSTEM_TEST_COMMIT_HR, self.getTestCodeCommit()))
        hrTests.extend(self.generateRunTestBuildParametersHr())
        if not self.ctestExecuted:
            hrTests.append("{}: {}".format(ERROR, CTEST_NOT_EXECUTED_ERROR))
        for me in self.maxscaleEntity:
            hrTests.append("{}: {}".format(MAXSCALE_FULL, me))
        return hrTests

    def generateMrResults(self, parsedCtestData):
        res = parsedCtestData
        res.update(self.generateRunTestBuildParametersMr())
        res.update({
            MAXSCALE_SYSTEM_TEST_COMMIT_MR: self.getTestCodeCommit(),
            MAXSCALE_COMMIT_MR: self.maxscaleCommit or NOT_FOUND,
            MAXSCALE_SOURCE_MR: self.maxscaleSource or NOT_FOUND,
            CMAKE_FLAGS_MR: self.maxscaleSource or NOT_FOUND,
            LOGS_DIR_MR: self.logsDir or NOT_FOUND,
            CTEST_ARGUMENTS_MR: self.generateCtestArguments(),
        })
        if not self.ctestExecuted:
            res.update({ERROR: CTEST_NOT_EXECUTED_ERROR})
        return json.dumps(res, sort_keys=True, indent=4)

    def showHrResults(self, parsedCtestData):
        print(self.generateHrResult(parsedCtestData))

    def showMrResults(self, parsedCtestData):
        print(self.generateMrResults(parsedCtestData))

    def saveResultsToFile(self):
        with open(self.args.output_log_file, "w") as file:
            ctestInfo = self.failedCtestInfo if self.args.only_failed else self.allCtestInfo
            file.writelines(NEW_LINE_JENKINS_FORMAT.join([BUILD_LOG_PARSING_RESULT]
                                                         + self.generateHrResult(ctestInfo)))

    def saveAllResultsToJsonFile(self):
        with open(self.args.output_log_json_file, "w") as file:
            file.writelines(self.generateMrResults(self.allCtestInfo))

    def showCtestParsedInfo(self):
        if not self.args.human_readable:
            self.showMrResults(self.failedCtestInfo if self.args.only_failed else self.allCtestInfo)
        else:
            self.showHrResults(self.failedCtestInfo if self.args.only_failed else self.allCtestInfo)

    def parse(self):
        self.parseCtestLog()
        self.showCtestParsedInfo()
        if self.args.output_log_file:
            self.saveResultsToFile()
        if self.args.output_log_json_file:
            self.saveAllResultsToJsonFile()


def main():
    args = options.parse_args()
    parser = CTestParser(args)
    parser.parse()


if os.path.samefile(__file__, sys.argv[0]):
    main()
