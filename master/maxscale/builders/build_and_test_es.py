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
            name=util.Interpolate("Building %(prop:image)s image"),
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
    for mtr_parameter in constants.mtrParams:
        factory.addStep(
            steps.Trigger(
                name="Running MTR with '{}'".format(mtr_parameter),
                schedulerNames=["run_mtr"],
                waitForFinish=True,
                set_properties={
                    "branch": util.Property("branch"),
                    "host": util.Property("host"),
                    "Image": util.Property("Image"),
                    "mtrParam": mtr_parameter,
                    "target": util.Property("target"),
                    "virtual_builder_name": util.Interpolate("run_mtr %(prop:Image)s {}".format(mtr_parameter))
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
