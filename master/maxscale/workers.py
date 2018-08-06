from buildbot.worker import Worker
from maxscale.config.workers import WORKER_CREDENTIALS


def workerConfiguration():
    """Create worker configuration for use in BuildBot configuration"""
    configuration = []
    for credentials in WORKER_CREDENTIALS:
        configuration.append(Worker(credentials["name"], credentials["password"]))
    return configuration


def workerNames():
    """Create a list of worker names that can be used in build configuration"""
    workers = []
    for credentials in WORKER_CREDENTIALS:
        workers.append(credentials["name"])
    return workers


def workerNamesByHost(host):
    """Creates a list of workers selected by a specific host"""
    return [worker["name"] for worker in WORKER_CREDENTIALS if worker["host"] is not host]
