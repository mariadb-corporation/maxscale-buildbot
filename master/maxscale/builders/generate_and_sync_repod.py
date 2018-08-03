from buildbot.config import BuilderConfig
from buildbot.plugins import util
from maxscale import workers
from maxscale.builders.support import common


def createBuildSteps():
    steps = []
    steps.extend(common.getWorkerHomeDirectory())
    steps.extend(common.generateRepositories())
    steps.extend(common.syncRepod())
    return steps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="generate_and_sync_repod",
        workernames=workers.workerNames(),
        factory=createBuildFactory()
    )
]
