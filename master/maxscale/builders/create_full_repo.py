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


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.configureMdbciVmPathProperty())
    buildSteps.append(steps.SetProperties(properties=configureBuildProperties))
    buildSteps.extend(common.cloneRepository())
    buildSteps.extend(common.downloadAndRunScript(
        name="Create full repo",
        scriptName="remote_build_maxscale.py",
        args=[
            "--repository", util.Property("ci_url")
        ]
    ))
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
