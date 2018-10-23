#!/usr/bin/env python3

import collections
import json
import os
import pytest
import re
import shutil
import subprocess
from itertools import zip_longest


def compareFiles(first, second):
    file1 = open(first, "r")
    file2 = open(second, "r")
    content1 = file1.readlines()
    content2 = file2.readlines()
    result = collections.Counter([line.strip('\n\\n ') for line in content1]) \
        == collections.Counter([line.strip('\n\\n ') for line in content2])
    if result:
        return result, ''
    return result, "Content of file {}: \n" \
                   "{}\n" \
                   "does not match content of file {}:\n" \
                   "{}".format(first, content1, second, content2)


def compareJsonFiles(first, second):
    file1 = open(first, "r")
    file2 = open(second, "r")
    content1 = json.load(file1)
    content2 = json.load(file2)
    result = content1 == content2
    if result:
        return result, ''
    return result, "Content of file {}: \n" \
                   "{}\n" \
                   "does not match content of file {}:\n" \
                   "{}".format(first, content1, second, content2)


def compareDirectories(first, second):
    for dir1, dir2 in zip_longest(os.walk(first), os.walk(second)):
        if dir1[0][len(first):] != dir2[0][len(second):] or dir1[1] != dir2[1]:
            return False
        for file1, file2 in zip_longest(dir1[2], dir2[2]):
            try:
                res = compareJsonFiles("{}/{}".format(dir1[0], file1), "{}/{}".format(dir2[0], file2))
                if not res[0]:
                    return res
            except json.decoder.JSONDecodeError:
                res = compareFiles("{}/{}".format(dir1[0], file1), "{}/{}".format(dir2[0], file2))
                if not res[0]:
                    return res

    return True, ''


def readLogsDir(source):
    logsDirRegex = re.compile(r"^Logs go to \/home\/vagrant\/LOGS\/(.+)$")
    with open(source) as file:
        for line in file:
            if logsDirRegex.search(line):
                return logsDirRegex.search(line).group(1).strip()


resultsDir = "{}/results".format(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def setupResultsDirectory(request, sources):
    if os.path.exists(resultsDir):
        shutil.rmtree(resultsDir)
    for source in sources:
        logsDir = readLogsDir(source)
        command = ["{}/../parser/parser.py".format(os.path.dirname(os.path.abspath(__file__))),
                   source, '-f', '-r', '-c', 'url', '-o', "{}/{}".format(resultsDir, logsDir)]
        subprocess.run(command)
        subprocess.run(command + ["-u"])


def test_compareHrResults(source, setupResultsDirectory):
    buildId = readLogsDir(source)
    result, message = compareFiles("{}/{}/ruby/results".format(resultsDir, buildId),
                                   "{}/{}/python/results".format(resultsDir, buildId))
    assert result, message


def test_compareMrResults(source, setupResultsDirectory):
    buildId = readLogsDir(source)
    result, message = compareJsonFiles("{}/{}/ruby/json".format(resultsDir, buildId),
                                       "{}/{}/python/json".format(resultsDir, buildId))
    assert result, message


def test_compareCoredumps(source, setupResultsDirectory):
    buildId = readLogsDir(source)
    result, message = compareFiles("{}/{}/ruby/coredump".format(resultsDir, buildId),
                                   "{}/{}/python/coredump".format(resultsDir, buildId))
    assert result, message


def test_compareCtestSublogs(source, setupResultsDirectory):
    buildId = readLogsDir(source)
    result, message = compareDirectories("{}/{}/ruby/ctest_sublogs".format(resultsDir, buildId),
                                         "{}/{}/python/ctest_sublogs".format(resultsDir, buildId))
    assert result, message
