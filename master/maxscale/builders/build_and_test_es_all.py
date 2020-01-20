from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants


def createBuildFactory():
    """
    Creates the source image and then starts builds for all the platforms
    """
    factory = util.BuildFactory()
    factory.addStep(
        steps.Trigger(
            name=util.Interpolate(
                "Creating source code package target '%(prop:target)s', branch '%(prop:branch)s'"
            ),
            schedulerNames=["build_es_star"],
            waitForFinish=True,
            set_properties={
                "branch": util.Property("branch"),
                "host": util.Property("host"),
                "repository": util.Property("repository"),
                "target": util.Property("target"),
            },
            haltOnFailure=True
        )
    )
    factory.addStep(
        common.TriggerWithVariable(
            name="Building on all platforms",
            schedulerNames=["build_and_test_es"],
            nameTemplate="Build and test image '{}'",
            propertyName="Image",
            propertyValues=constants.images,
            waitForFinish=True,
            set_properties={
                "branch": util.Property("branch"),
                "BuildType": util.Property("BuildType"),
                "host": util.Property("host"),
                "target": util.Property("target"),
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
