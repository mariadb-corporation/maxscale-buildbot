import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util
from maxscale import workers
from . import support_new as support


ENVIRONMENT = {
    "JOB_NAME": util.Property("buildername"),
    "BUILD_ID": util.Interpolate('%(prop:buildnumber)s'),
    "BUILD_NUMBER": util.Interpolate('%(prop:buildnumber)s'),
    "MDBCI_VM_PATH": util.Property('MDBCI_VM_PATH'),
    "box": util.Property('box'),
    "target": util.Property('target'),
    "cmake_flags": util.Property('cmake_flags'),
    "do_not_destroy_vm": util.Property('do_not_destroy_vm'),
    "build_experimental": util.Property('build_experimental'),
    "try_already_running": util.Property('try_already_running'),
    "run_upgrade_test": util.Property('run_upgrade_test'),
    "old_target": util.Property('old_target'),
    "ci_url": util.Property('ci_url')
}


def remoteBuildMaxscale():
    """This script will be run on the worker"""
    if not os.path.exists("BUILD/mdbci"):
        os.mkdir("default-maxscale-branch")
        os.chdir("default-maxscale-branch")
        os.system("git clone {}".format(repository))
        os.chdir("..")
    if not os.path.isdir("BUILD"):
        shutil.copytree("default-maxscale-branch/MaxScale/BUILD", ".")
    if not os.path.isdir("BUILD/mdbci"):
        shutil.copytree("default-maxscale-branch/MaxScale/BUILD/mdbci", "BUILD/")
    buildScript = "./BUILD/mdbci/build.sh"
    os.execl(buildScript, buildScript)


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(support.configureMdbciVmPathProperty())
    buildSteps.extend(support.cloneRepository())
    buildSteps.extend(support.executePythonScript(
        "Build MaxScale using MDBCI", remoteBuildMaxscale))
    buildSteps.extend(support.cleanBuildDir())
    buildSteps.extend(support.cleanBuildIntermediates())
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_new",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT
    )
]
