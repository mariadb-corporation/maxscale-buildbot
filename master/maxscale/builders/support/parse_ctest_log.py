import os
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


parser = argparse.ArgumentParser(description="CTest parser usage:")
parser.add_argument(LOG_FILE_OPTION, help="CTEST LOG FILE PATH")
parser.add_argument("-f", ONLY_FAILED_OPTION, action="store_true", help="PARSE ONLY FAILED TESTS")
parser.add_argument("-r", HUMAN_READABLE_OPTION, action="store_true", help="HUMAN READABLE OUTPUT")
parser.add_argument("-o", OUTPUT_LOG_FILE_OPTION, metavar="file_path",
                    help="CTEST PARSER OUTPUT LOG FILE HUMAN READABLE FOR JENKINS (environmental variable format)")
parser.add_argument("-j", OUTPUT_LOG_JSON_FILE_OPTION, metavar="json_file_path",
                    help="CTEST PARSER OUTPUT LOG JSON FILE (there will be saved all test results - passed and failed)")


def main():
    args = parser.parse_args()


if os.path.samefile(__file__, sys.argv[0]):
    main()
