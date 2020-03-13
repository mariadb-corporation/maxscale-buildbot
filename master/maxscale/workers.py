from buildbot.worker import Worker
from maxscale.config.workers import WORKER_CREDENTIALS


def workerConfiguration():
    """Create worker configuration for use in BuildBot configuration"""
    configuration = []
    for credentials in WORKER_CREDENTIALS:
        configuration.append(Worker(credentials["name"], credentials["password"]))
    return configuration


def workerNames(host=""):
    """Create a list of worker names that can be used in build configuration"""
    workers = []
    for credentials in WORKER_CREDENTIALS:
        if host in credentials["host"]:
            workers.append(credentials["name"])
    return workers


def workersOnHosts(*hosts):
    """
    Create a list of worker names that run on the specified hosts
    hosts (list): names of the host names to use
    """
    workers = []
    for credentials in WORKER_CREDENTIALS:
        if credentials["host"] in hosts:
            workers.append(credentials["name"])
    return workers


def workerToHostMap():
    """Creates dictionary with worker name mapped to host"""
    workerToHost = {}
    for credentials in WORKER_CREDENTIALS:
        workerToHost[credentials["name"]] = credentials["host"]
    return workerToHost
