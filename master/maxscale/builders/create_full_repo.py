import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common, support

ENVIRONMENT = {
    "JOB_NAME": util.Property("buildername"),
    "BUILD_ID": util.Interpolate('%(prop:buildnumber)s'),
    "BUILD_NUMBER": util.Interpolate('%(prop:buildnumber)s'),
    "MDBCI_VM_PATH": util.Property('MDBCI_VM_PATH'),
    "box": util.Property('box'),
    "target": util.Property('target'),
    "do_not_destroy_vm": util.Property('do_not_destroy_vm'),
    "ci_url": util.Property('ci_url'),
    "major_ver": util.Property('major_ver')
}


@util.renderer
def configureBuildProperties(properties):
    return {
        "mdbciConfig": util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:box)s-%(prop:buildername)s-%(prop:buildnumber)s")
    }


def remoteBuildMaxscale():
    """This script will be run on the worker"""
    if not os.path.exists("BUILD/mdbci"):
        os.mkdir("default-maxscale-branch")
        os.chdir("default-maxscale-branch")
        subprocess.run(["git", "clone", repository])
        os.chdir("..")
    if not os.path.isdir("BUILD"):
        shutil.copytree("default-maxscale-branch/MaxScale/BUILD", ".")
    if not os.path.isdir("BUILD/mdbci"):
        shutil.copytree("default-maxscale-branch/MaxScale/BUILD/mdbci", "BUILD/")
    results = subprocess.run(["BUILD/mdbci/create_full_repo.sh"])
    sys.exit(results.returncode)


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.configureMdbciVmPathProperty())
    buildSteps.append(steps.SetProperties(properties=configureBuildProperties))
    buildSteps.extend(common.cloneRepository())
    buildSteps.extend(support.executePythonScript(
        "Create full repo", remoteBuildMaxscale))
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
        name="create_full_repo",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        tags=["create_full_repo"],
        env=ENVIRONMENT,
        collapseRequests=False,
    )
]
