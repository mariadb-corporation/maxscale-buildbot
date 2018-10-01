import os
import re
import sys
import argparse

LOG_FILE_OPTION = 'log-file'
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
        self.allCtestInfo = {}
        self.failedCtestInfo = {}
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
        ctestStartLine = 0
        maxscaleVersionStartFound = False
        maxscaleVersionEndFound = False

        file = open(self.args.log_file, encoding="UTF-8")
        for line in file:
            if maxscaleVersionEndRegex.match(line):
                maxscaleVersionEndFound = True
            if maxscaleVersionStartFound and not maxscaleVersionEndFound and line.replace("\n", ""):
                self.maxscaleEntity.append(line.replace("\n", ""))
            if maxscaleVersionStartRegex.match(line):
                maxscaleVersionStartFound = True
            if maxscaleCommitRegex.match(line) and not self.maxscaleCommit:
                self.maxscaleCommit = maxscaleCommitRegex.match(line)[0]
            if maxscaleSourceRegex.match(line) and not self.maxscaleSource:
                self.maxscaleSource = maxscaleSourceRegex.match(line)[0].strip()
            if logsFirRegex.match(line) and not self.logsDir:
                self.logsDir = logsFirRegex.match(line)[0].strip()
            if ctestFirstLineRegex:
                self.ctestExecuted = True
                break
            ctestStartLine += 1

        if self.ctestExecuted:
            ctestLog = file.readlines()[ctestStartLine:-1]
            ctestEndLine = 0
            for line in ctestLog:
                if ctestLastLineRegex.match(line):
                    self.ctestSummary = line
                    break
                ctestEndLine += 1
            ctestLog = ctestLog[:ctestEndLine]
            testQuantity = ctestLastLineRegex.match(ctestLog[-1])[0]
            self.findTestsInfo(ctestLog)
            self.allCtestInfo.update({TESTS_COUNT: testQuantity})
            self.failedCtestInfo.update({TESTS_COUNT: testQuantity})
        else:
            self.ctestSummary = CTEST_SUMMARY_NOTE_FOUND
            self.allCtestInfo = {TESTS_COUNT: NOT_FOUND, FAILED_TESTS_COUNT: NOT_FOUND, TESTS: []}
            self.failedCtestInfo = {TESTS_COUNT: NOT_FOUND, FAILED_TESTS_COUNT: NOT_FOUND, TESTS: []}

    def findTestsInfo(self, ctestLog):



def main():
    args = options.parse_args()
    CTestParser(args)


if os.path.samefile(__file__, sys.argv[0]):
    main()
