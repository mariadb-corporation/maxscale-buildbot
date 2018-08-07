#!/usr/bin/env python3

import sys
import os.path
import argparse
import getpass
import socket
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
    hosts = []
    for hostConfiguration in workers.WORKER_CREDENTIALS:
        if arguments.host is not None and hostConfiguration["host"] != arguments.host:
            continue
        ipAddress = determineIP(hostConfiguration["host"], arguments.domain)
        if ipAddress is None:
            continue
        hosts.append({
            "ip": ipAddress,
            "config": hostConfiguration
        })
    return hosts

def installWorkers(hosts):
    print(hosts)
    pass


def main():
    arguments = parseArguments()
    actions = {
        'install': installWorkers
    }
    action = actions.get(arguments.action)
    if action is None:
        print("Unknown action '{}'.".format(arguments.action))
        exit(1)
    hosts = determineHosts(arguments)
    action(hosts)


if __name__ == "__main__":
    main()
