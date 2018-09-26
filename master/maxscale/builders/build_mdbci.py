import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common, support

ENVIRONMENT = {
    "JOB_NAME": util.Property("buildername"),
    "BUILD_ID": util.Interpolate('%(prop:buildnumber)s'),
    "BUILD_NUMBER": util.Interpolate('%(prop:buildnumber)s'),
}


@util.renderer
def configureBuildProperties(properties):
    return {
        "mdbciConfig": util.Interpolate("%(prop:buildername)s-%(prop:buildnumber)s")
    }


def remoteBuildMdbci():
    """This script will be run on the worker"""
    os.chdir("package")
    results = subprocess.run(["build.sh"])
    sys.exit(results.returncode)


def createBuildSteps():
    buildSteps = []
    buildSteps.append(steps.SetProperties(properties=configureBuildProperties))
    buildSteps.extend(common.cloneRepository())
    buildSteps.extend(support.executePythonScript(
        "Build MDBCI", remoteBuildMdbci))
    buildSteps.extend(common.cleanBuildDir())
    buildSteps.extend(common.destroyVirtualMachine())
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_mdbci",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False,
    )
]
