import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common, support

ENVIRONMENT = {
    "version_number": util.Property("version_number"),
}


def copyToDl02():
    """Copy stuff to dl02.mariadb.com"""
    return [steps.ShellCommand(
        name="Copy stuff to dl02.mariadb.com",
        command=["~/.config/mdbci/publish_release.sh", util.Property("version_number")],
        alwaysRun=True)]


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(copyToDl02())
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    factory.addSteps(createBuildSteps())
    return factory


BUILDERS = [
    BuilderConfig(
        name="publish_release",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["publish_release"],
        env=ENVIRONMENT,
        collapseRequests=False
    )
]
