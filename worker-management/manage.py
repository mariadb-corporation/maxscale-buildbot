#!/usr/bin/env python3

import sys
import os.path
import argparse
import getpass
import socket
import paramiko
import logging

sys.path.append(os.path.abspath("{}/../../master/".format(__file__)))
import maxscale.config.workers as workers


def parseArguments():
    parser = argparse.ArgumentParser(description="A tool to install, restart the BuildBot worker instances.")
    parser.add_argument("action", help="Action to perform, install for example.")
    parser.add_argument("--host", help="Host to manage.")
    parser.add_argument("--user", help="User to use during the SSH connection to host.", default=getpass.getuser())
    parser.add_argument("--domain", help="Default domain for hosts", default="mariadb.com")
    return parser.parse_args()


def determineIP(host, domain):
    possibleHosts = [
        host,
        "{}.{}".format(host, domain)
    ]
    for checkHost in possibleHosts:
        try:
            info = socket.gethostbyname(checkHost)
        except BaseException:
            continue
        return info
    return None


def determineHosts(arguments):
    hosts = {}
    for hostConfiguration in workers.WORKER_CREDENTIALS:
        if arguments.host is not None and hostConfiguration["host"] != arguments.host:
            continue
        ipAddress = determineIP(hostConfiguration["host"], arguments.domain)
        if ipAddress is None:
            continue
        if ipAddress in hosts:
            hosts[ipAddress].append(hostConfiguration)
        else:
            hosts[ipAddress] = [hostConfiguration]
    return hosts


def runCommand(sshClient, command):
    stdin, stdout, stderr = sshClient.exec_command(command)
    stdin.close()
    stdoutContents = stdout.readlines()
    stderrContents = stderr.readlines()
    return ["".join(stdoutContents).strip(), "".join(stderrContents).strip()]


PYTHON_VENV = "~/buildbot-virtual-env"
WORKERS_DIR = "~/buildbot-workers"
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def setupVirtualEnv(sshClient):
    _, stderr = runCommand(sshClient, "ls -ld {}".format(PYTHON_VENV))
    if stderr:
        logging.info("Creating python virtual environment in {}".format(PYTHON_VENV))
        runCommand(sshClient, "python3 -m virtualenv -p /usr/bin/python3 {}".format(PYTHON_VENV))
    logging.info("Installing latest version of requirements")
    absolutePythonEnvDir, _ = runCommand(sshClient, "cd {}; pwd".format(PYTHON_VENV))
    sftClient = sshClient.open_sftp()
    sftClient.put("{}/requirements-worker.txt".format(CURRENT_DIR), "{}/requirements.txt".format(absolutePythonEnvDir))
    runCommand(sshClient, "{}/bin/pip3 install -U -r {}/requirements.txt".format(PYTHON_VENV, PYTHON_VENV))


def createWorkerConfig(sshClient, config):
    print(config)


def installWorkers(hosts, username):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    for hostIp in hosts:
        logging.info("Configuring host {}".format(hostIp))
        client.connect(hostIp, username=username)
        setupVirtualEnv(client)
        for worker in hosts[hostIp]:
            createWorkerConfig(client, worker)
        client.close()
    pass


def main():
    logging.basicConfig(level=logging.INFO)
    arguments = parseArguments()
    actions = {
        'install': installWorkers
    }
    action = actions.get(arguments.action)
    if action is None:
        logging.error("Unknown action '{}'.".format(arguments.action))
        exit(1)
    hosts = determineHosts(arguments)
    action(hosts, arguments.user)


if __name__ == "__main__":
    main()
