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
        "mdbciConfig": util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:box)s-%(prop:buildername)s-%(prop:buildnumber)s")
    }

def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.configureMdbciVmPathProperty())
    buildSteps.append(steps.SetProperties(properties=configureBuildProperties))
    buildSteps.extend(common.cloneRepository())
    buildSteps.append(steps.ShellCommand(
        name="Build MaxScale using MDBCI",
        command=['BUILD/mdbci/build.sh'],
        timeout=3600,
        workdir=util.Interpolate("%(prop:builddir)s")
    ))
    buildSteps.extend(common.cleanBuildDir())
    buildSteps.extend(common.destroyVirtualMachine())
    buildSteps.extend(common.removeLock())
    cmd = 'ssh vagrant@max-tst-01.mariadb.com mkdir -p ./repository/%(prop:target)s/mariadb-maxscale'
    buildSteps.append(steps.ShellCommand(
        name="Make dir for build results on the repo server",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
    ))
    cmd = 'rsync -avz --progress -e ssh ~/repository/%(prop:target)s/mariadb-maxscale/ vagrant@max-tst-01.mariadb.com:./repository/%(prop:target)s/mariadb-maxscale/'
    buildSteps.append(steps.ShellCommand(
        name="Rsync builds results to the repo server",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
    ))
    cmd = '~/mdbci/mdbci generate-product-repositories --product maxscale_ci --product-version %(prop:target)s'
    buildSteps.append(steps.ShellCommand(
        name="Generate new repo descriptions",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
    ))
    buildSteps.extend(common.syncRepod())
    buildSteps.append(steps.ShellCommand(
        name="Upgrade test",
        command=['BUILD/mdbci/upgrade_test.sh'],
        timeout=1800,
        doStepIf = (util.Property('run_upgrade_test') == 'yes'),
        workdir=util.Interpolate("%(prop:builddir)s")
    ))
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
        nextBuild=common.assignBuildRequest,
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False,
        defaultProperties={
            "try_already_running": None
        }
    )
]
