from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants


def createBuildFactory():
    """
    Creates build factory containing steps
    which triggers build_es_bin scheduler and run_mtr with all parameters
    """
    factory = util.BuildFactory()
    factory.addStep(
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
            },
            haltOnFailure=True
        )
    )
    factory.addStep(common.TriggerWithVariable(
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
        })
    )
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_es",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["build"],
        collapseRequests=False
    )
]
