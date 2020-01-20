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
    for image in constants.images:
        factory.addStep(
            steps.Trigger(
                name=util.Interpolate(
                    "Build and test target '%(prop:target)s', build type '%(prop:BuildType)s', image '{}'".format(image)
                ),
                schedulerNames=["build_and_test_es"],
                waitForFinish=True,
                set_properties={
                    "branch": util.Property("branch"),
                    "BuildType": util.Property("BuildType"),
                    "host": util.Property("host"),
                    "Image": image,
                    "target": util.Property("target"),
                    "virtual_builder_name": "build_and_test_es {}".format(image),
                }
            )
        )
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_es_all",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["build"],
        collapseRequests=False
    )
]
