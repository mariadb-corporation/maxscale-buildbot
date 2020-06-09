from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants

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


@util.renderer
def configureBuildProperties(properties):
    return {
        "mdbciConfig": util.Interpolate(
            "%(prop:MDBCI_VM_PATH)s/%(prop:box)s-%(prop:buildername)s-%(prop:buildnumber)s"),
        "upload_server": constants.UPLOAD_SERVERS[properties.getProperty("host")],
    }


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.configureMdbciVmPathProperty())
    buildSteps.append(steps.SetProperties(properties=configureBuildProperties))
    buildSteps.extend(common.cloneRepository())
    buildSteps.append(steps.ShellCommand(
        name="Build MaxScale using MDBCI",
        command=['/bin/bash', '-c', 'BUILD/mdbci/build.sh || BUILD/mdbci/build.sh'],
        timeout=3600,
        workdir=util.Interpolate("%(prop:builddir)s/build")
    ))
    buildSteps.extend(common.destroyVirtualMachine())
    buildSteps.append(common.runSshCommand(
        name="Make dir for build results on the repo server",
        host=util.Property("upload_server"),
        command=["mkdir", "-p", util.Interpolate(constants.UPLOAD_PATH + '/%(prop:target)s')],
    ))
    buildSteps.append(common.rsyncViaSsh(
        name="Rsync builds results to the repo server",
        local=util.Interpolate("%(prop:HOME)s/repository/%(prop:target)s/mariadb-maxscale/"),
        remote=util.Interpolate("%(prop:upload_server)s:" + constants.UPLOAD_PATH + "/%(prop:target)s/")
    ))
    buildSteps.append(common.generateMdbciRepositoryForTarget())
    buildSteps.extend(common.syncRepod())
    buildSteps.append(steps.ShellCommand(
        name="Upgrade test",
        command=['BUILD/mdbci/upgrade_test.sh'],
        timeout=1800,
        doStepIf=(util.Property('run_upgrade_test') == 'yes'),
        workdir=util.Interpolate("%(prop:builddir)s/build")
    ))
    buildSteps.extend(common.cleanBuildDir())
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False,
        defaultProperties={
            "try_already_running": None
        }
    )
]
