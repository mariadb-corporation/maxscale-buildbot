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


def determineHost(host, domain):
    possibleHosts = [
        host,
        "{}.{}".format(host, domain)
    ]
    for checkHost in possibleHosts:
        try:
            info = socket.gethostbyname(checkHost)
        except BaseException:
            continue
        return checkHost
    return None


def determineHosts(arguments):
    hosts = {}
    for hostConfiguration in workers.WORKER_CREDENTIALS:
        if arguments.host is not None and hostConfiguration["host"] != arguments.host:
            continue
        host = determineHost(hostConfiguration["host"], arguments.domain)
        if host is None:
            continue
        if host in hosts:
            hosts[host].append(hostConfiguration)
        else:
            hosts[host] = [hostConfiguration]
    return hosts


def runCommand(sshClient, command):
    logging.debug("Calling command '{}'".format(command))
    stdin, stdout, stderr = sshClient.exec_command(command)
    stdin.close()
    stdoutContents = stdout.readlines()
    stderrContents = stderr.readlines()
    stdoutText = "".join(stdoutContents).strip()
    stderrText = "".join(stderrContents).strip()
    logging.debug("Stdout:\n{}".format(stdoutText))
    logging.debug("Stderr:\n{}".format(stderrText))
    return [stdoutText, stderrText]


def isDirectoryAbsent(sshClient, directory):
    _, stderr = runCommand(sshClient, "ls -ld {}".format(directory))
    if stderr:
        return True
    else:
        return False


PYTHON_VENV = "~/buildbot-virtual-env"
WORKERS_DIR = "~/buildbot-workers"
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def setupVirtualEnv(sshClient):
    if isDirectoryAbsent(sshClient, PYTHON_VENV):
        logging.info("Creating python virtual environment in {}".format(PYTHON_VENV))
        runCommand(sshClient, "python3 -m virtualenv -p /usr/bin/python3 {}".format(PYTHON_VENV))
    logging.info("Installing latest version of requirements")
    absolutePythonEnvDir, _ = runCommand(sshClient, "cd {}; pwd".format(PYTHON_VENV))
    sftClient = sshClient.open_sftp()
    sftClient.put("{}/requirements-worker.txt".format(CURRENT_DIR), "{}/requirements.txt".format(absolutePythonEnvDir))
    runCommand(sshClient, "{}/bin/pip3 install -U -r {}/requirements.txt".format(PYTHON_VENV, PYTHON_VENV))


def createWorkerConfig(sshClient, config, masterHost):
    logging.info("Creating configuration for worker '{}'.".format(config["name"]))
    runCommand(sshClient, "mkdir -p {}".format(WORKERS_DIR))
    runCommand(sshClient, "rm -rf {dir}/{name}".format(dir=WORKERS_DIR, **config))
    runCommand(sshClient, "{venv}/bin/buildbot-worker create-worker --umask=0o002 {dir}/{name} {server} {name} {password}".format(
        venv=PYTHON_VENV, dir=WORKERS_DIR, server=masterHost, **config))
    runCommand(sshClient, "echo '{host}' > {dir}/{name}/info/host".format(dir=WORKERS_DIR, **config))


def installWorkers(hosts, arguments):
    stopWorkers(hosts, arguments)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    for hostIp in hosts:
        logging.info("Configuring host {}".format(hostIp))
        client.connect(hostIp, username=arguments.user)
        setupVirtualEnv(client)
        for worker in hosts[hostIp]:
            createWorkerConfig(client, worker, arguments.master)
        client.close()


def callBuildbotAction(action, hosts, arguments):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    for hostIp in hosts:
        logging.info("Executing action '{}' workers on host '{}'".format(action, hostIp))
        client.connect(hostIp, username=arguments.user)
        for worker in hosts[hostIp]:
            if isDirectoryAbsent(client, "{dir}/{name}".format(dir=WORKERS_DIR, **worker)):
                logging.debug("Worker '{name}' configuration does not exist, doing nothing".format(**worker))
                continue
            runCommand(client, "{venv}/bin/buildbot-worker {action} {dir}/{name}".format(
                venv=PYTHON_VENV, dir=WORKERS_DIR, action=action, **worker))

def restartWorkers(hosts, arguments):
    callBuildbotAction("restart", hosts, arguments)


def stopWorkers(hosts, arguments):
    callBuildbotAction("stop", hosts, arguments)


def startWorkers(hosts, arguments):
    callBuildbotAction("start", hosts, arguments)


AVAILABLE_ACTIONS = {
    "install": installWorkers,
    "restart": restartWorkers,
    "stop": stopWorkers,
    "start": startWorkers
}


def parseArguments():
    parser = argparse.ArgumentParser(description="A tool to install, restart the BuildBot worker instances.")
    parser.add_argument("action", help="Action to perform, install for example.", choices=AVAILABLE_ACTIONS.keys())
    parser.add_argument("--host", help="Host to manage.")
    parser.add_argument("--user", help="User to use during the SSH connection to host.", default=getpass.getuser())
    parser.add_argument("--domain", help="Default domain for hosts", default="mariadb.com")
    parser.add_argument("--master", help="Domain name of the master to configure on workers", default="maxscale-ci.mariadb.com")
    parser.add_argument("--debug", help="Show debug output", dest="debug", action="store_true")
    parser.set_defaults(debug=False)
    return parser.parse_args()


def main():
    arguments = parseArguments()
    if arguments.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    action = AVAILABLE_ACTIONS.get(arguments.action)
    if action is None:
        logging.error("Unknown action '{}'.".format(arguments.action))
        exit(1)
    hosts = determineHosts(arguments)
    action(hosts, arguments)


if __name__ == "__main__":
    main()
