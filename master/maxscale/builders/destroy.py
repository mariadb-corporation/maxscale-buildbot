from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.plugins import steps, util
from maxscale import workers
from maxscale.builders.support import common


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.configureMdbciVmPathProperty())
    buildSteps.append(steps.SetProperty(
        name="Set mdbci configuration path",
        property="mdbciConfig",
        value=util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:name)s")
    ))
    buildSteps.extend(common.destroyVirtualMachine())
    return buildSteps


def createFactory():
    factory = BuildFactory()
    factory.addSteps(createBuildSteps())
    return factory


BUILDERS = [
    BuilderConfig(
        name="destroy",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=createFactory(),
        tags=["destroy"],
    )
]
