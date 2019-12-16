from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.plugins import steps, util
from maxscale import workers
from maxscale.builders.support import common, support

def remoteMTR():
    """This script will be run on the worker"""
    results = subprocess.run(["/home/vagrant/terraform/run.sh"])
    sys.exit(results.returncode)

def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.configureMdbciVmPathProperty())
    buildSteps.append(steps.SetProperty(
        name="MTR expamle with GCloud",
        property="mdbciConfig",
        value=util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:name)s")
    ))
    buildSteps.extend(support.executePythonScript(
        "Run MTR", remoteMTR))
    return buildSteps


def createFactory():
    factory = BuildFactory()
    factory.addSteps(createBuildSteps())
    return factory


BUILDERS = [
    BuilderConfig(
        name="run_mtr",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=createFactory(),
        tags=["mtr"],
    )
]
