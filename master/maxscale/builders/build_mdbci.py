import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common, support
from buildbot.steps.shell import ShellCommand

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
    os.chdir("../build/package")
    results = subprocess.run("./build.sh " + str(buildnumber), shell=True)
    sys.exit(results.returncode)


def publishMdbci():
    return [steps.ShellCommand(
        name="Copy MDBCI AppImage to CI repository",
        command=util.Interpolate("cp %(prop:builddir)s/build/package/build/out/* $HOME/%(prop:repo_path)s"),
        alwaysRun=False)]


def createBuildSteps():
    buildSteps = []
    buildSteps.append(steps.SetProperties(properties=configureBuildProperties))
    buildSteps.extend(common.cloneRepository())
    buildSteps.extend(support.executePythonScript(
        "Build MDBCI", remoteBuildMdbci))
    buildSteps.extend(publishMdbci())
    buildSteps.extend(common.cleanBuildDir())
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
