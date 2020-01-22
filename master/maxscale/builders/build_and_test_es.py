from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants

ENVIRONMENT = {
    "target": util.Property('target'),
    "Image":  util.Property('Image'),
    "buildnumber": util.Interpolate('%(prop:buildnumber)s'),
}


def createBuildSteps():
    """
    Creates build steps
    which triggers build_es_bin scheduler and run_mtr with all parameters
    """
    buildSteps = []
    buildSteps.extend(common.downloadAndRunMTRScript(
         "mtr/start_vm.sh",
          name=util.Interpolate("Start VM"),
          haltOnFailure=True,
          workdir=util.Interpolate("%(prop:builddir)s"),
    ))
    buildSteps.append(
        steps.Trigger(
            name=util.Interpolate("Building image '%(prop:Image)s'"),
            schedulerNames=["build_es_bin"],
            waitForFinish=True,
            set_properties={
                "branch": util.Property("branch"),
                "BuildType": util.Property("BuildType"),
                "host": util.Property("host"),
                "Image": util.Property("Image"),
                "target": util.Property("target"),
                "buildID": util.Interpolate('%(prop:buildnumber)s'),
            },
            haltOnFailure=True
        )
    )
    buildSteps.append(common.TriggerWithVariable(
        name="Run MTR tests with different parameters",
        schedulerNames=["run_mtr"],
        waitForFinish=True,
        propertyName="mtrParam",
        propertyValues=constants.mtrParams,
        nameTemplate="Running MTR with '{}'",
        set_properties={
            "branch": util.Property("branch"),
            "host": util.Property("host"),
            "Image": util.Property("Image"),
            "target": util.Property("target"),
            "buildID": util.Interpolate('%(prop:buildnumber)s'),
        }
    ))
    buildSteps.extend(common.downloadAndRunMTRScript(
        "mtr/kill_vm.sh",
         name=util.Interpolate("Kill VM"),
         workdir=util.Interpolate("%(prop:builddir)s"),
         haltOnFailure=True,
         alwaysRun=True
    ))
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_es",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        env=ENVIRONMENT,
        tags=["build"],
        collapseRequests=False
    )
]
