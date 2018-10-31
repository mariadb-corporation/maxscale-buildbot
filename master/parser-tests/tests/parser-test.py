#!/usr/bin/env python3

import collections
import json
import mysql.connector
import os
import pytest
import re
import shutil
import subprocess
from configparser import ConfigParser
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


def readDatabaseConfiguration(filename='/home/maksim/build_parser_db_password', section='client'):
    config = ConfigParser()
    config.read(filename)
    db = {}
    if config.has_section(section):
        for item in config.items(section):
            db[item[0]] = item[1]
    else:
        raise Exception("{} not found in the {} file".format(section, filename))
    return db


resultsDir = "{}/results".format(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def database():
    dbName = 'parser_test_results_db'
    config = readDatabaseConfiguration()
    testdb = mysql.connector.connect(**config)
    cursor = testdb.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(dbName))
    cursor.execute("use {}".format(dbName))
    cursor.execute('CREATE TABLE IF NOT EXISTS test_run (id int(11) PRIMARY KEY, jenkins_id int(11), '
                   'start_time datetime, target varchar(256), box varchar(256), product varchar(256), '
                   'mariadb_version varchar(256), test_code_commit_id varchar(256), maxscale_commit_id varchar(256), '
                   'job_name varchar(256), cmake_flags text, maxscale_source varchar(256), logs_dir varchar(256))')

    cursor.execute('CREATE TABLE IF NOT EXISTS results(id int(11), FOREIGN KEY (id) REFERENCES test_run(id) '
                   'ON DELETE CASCADE, test varchar(256), result int(11), '
                   'test_time float, core_dump_path varchar(500))')
    cursor.close()
    yield testdb

    cursor = testdb.cursor()
    cursor.execute("DROP DATABASE {}".format(dbName))
    cursor.close()
    testdb.close()


@pytest.fixture(scope="module")
def resultsTableColumns(database):
    cursor = database.cursor()
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                   "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'results'")
    columns = cursor.fetchall()
    cursor.close()
    return [column[0] for column in columns]


@pytest.fixture(scope="module")
def testRunTableColumns(database):
    cursor = database.cursor()
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                   "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'test_run'")
    columns = cursor.fetchall()
    cursor.close()
    return [column[0] for column in columns]


def setup_module(module):
    if os.path.exists(resultsDir):
        shutil.rmtree(resultsDir)


@pytest.fixture(scope="session")
def buildId(request, source):
    yield readLogsDir(source)


@pytest.fixture(scope="session")
def parseSource(request, source):
    logsDir = readLogsDir(source)
    command = ["{}/../parser/parser.py".format(os.path.dirname(os.path.abspath(__file__))),
               source, '-f', '-r', '-c', 'url', '-o', "{}/{}".format(resultsDir, logsDir)]
    subprocess.run(command)
    subprocess.run(command + ["-u"])


def test_compareHrResults(buildId, parseSource):
    if not os.path.exists("{}/{}/".format(resultsDir, buildId)):
        pytest.skip("Test run failed and didn't produces any results")
    result, message = compareFiles("{}/{}/ruby/results".format(resultsDir, buildId),
                                   "{}/{}/python/results".format(resultsDir, buildId))
    assert result, message


def test_compareMrResults(buildId, parseSource):
    if not os.path.exists("{}/{}/".format(resultsDir, buildId)):
        pytest.skip("Test run failed and didn't produces any results")
    result, message = compareJsonFiles("{}/{}/ruby/json".format(resultsDir, buildId),
                                       "{}/{}/python/json".format(resultsDir, buildId))
    assert result, message


def test_compareCoredumps(buildId, parseSource):
    if not os.path.exists("{}/{}/".format(resultsDir, buildId)):
        pytest.skip("Test run failed and didn't produces any results")
    result, message = compareFiles("{}/{}/ruby/coredump".format(resultsDir, buildId),
                                   "{}/{}/python/coredump".format(resultsDir, buildId))
    assert result, message


def test_compareCtestSublogs(buildId, parseSource):
    if not os.path.exists("{}/{}/".format(resultsDir, buildId)):
        pytest.skip("Test run failed and didn't produces any results")
    result, message = compareDirectories("{}/{}/ruby/ctest_sublogs".format(resultsDir, buildId),
                                         "{}/{}/python/ctest_sublogs".format(resultsDir, buildId))
    assert result, message


def test_compareDatabaseResults(buildId, parseSource, database, resultsTableColumns, testRunTableColumns):
    if not os.path.exists("{}/{}/".format(resultsDir, buildId)):
        pytest.skip("Test run failed and didn't produces any results")

    cursor = database.cursor()
    scriptsPath = "{}/../parser/".format(os.path.dirname(os.path.abspath(__file__)))

    subprocess.run(["{}/ruby-scripts/write_build_results.rb".format(scriptsPath),
                    "-f", "{}/{}/ruby/json".format(resultsDir, buildId)], stdout=subprocess.DEVNULL)
    cursor.execute("SELECT {} FROM results".format(", ".join(resultsTableColumns)))
    rubyResults = cursor.fetchall()
    cursor.execute("SELECT {} FROM test_run".format(", ".join(testRunTableColumns)))
    rubyTestRun = cursor.fetchall()
    cursor.execute('DELETE FROM test_run')
    database.commit()

    subprocess.run(["{}/python-scripts/write_build_results.py".format(scriptsPath),
                    "{}/{}/ruby/json".format(resultsDir, buildId)], stdout=subprocess.DEVNULL)
    cursor.execute("SELECT {} FROM results".format(", ".join(resultsTableColumns)))
    pythonResults = cursor.fetchall()
    cursor.execute("SELECT {} FROM test_run".format(", ".join(testRunTableColumns)))
    pythonTestRun = cursor.fetchall()
    cursor.execute('DELETE FROM test_run')
    database.commit()

    assert rubyTestRun == pythonTestRun, \
        "test_run rows created by Ruby parser:\n{}\n" \
        "does not match rows created by Python parser:\n{}"\
        .format(rubyTestRun, pythonTestRun)

    assert rubyResults == pythonResults, \
        "results rows created by Ruby parser:\n{}\n" \
        "does not match rows created by Python parser:\n{}"\
        .format(rubyResults, pythonResults)

    cursor.close()
