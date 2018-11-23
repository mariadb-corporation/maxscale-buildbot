import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common
from maxscale.change_source.maxscale import get_test_set_by_branch

COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES = [
    "branch",
    "repository",
    "cmake_flags",
    "build_experimental",
    "product",
    "version",
    "ci_url",
    "host",
    "owners",
]


@util.renderer
def renderTestSet(properties):
    """
    Returns test set value if it's present, otherwise returns test set filtered by branch
    :param properties:
    :return: Test set
    """
    return properties.getProperty("test_set") \
        or get_test_set_by_branch(properties.getProperty('branch'))


def createFactory():
    factory = BuildFactory()
    factory.addSteps(common.setMissingTarget())
    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler. Build CentOS",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES,
        set_properties={
            "box": util.Property("box"),
            'try_already_running': 'yes',
            "target": util.Property("target"),
            'virtual_builder_name': util.Interpolate('Build for %(prop:box)s'),
        }
    ))
    factory.addStep(steps.Trigger(
        name="Call the 'run_test_snapshot' scheduler. Run functional tests",
        schedulerNames=['run_test_snapshot'],
        waitForFinish=True,
        copy_properties=COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES,
        set_properties={
            "box": util.Property("box"),
            "target": util.Property("target"),
            "test_branch": util.Property("branch"),
            "test_set": renderTestSet,
            "backend_ssl": util.Property("backend_ssl"),
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_snapshot",
        workernames=workers.workerNames(),
        nextWorker=common.assignBestHost,
        nextBuild=common.assignBuildRequest,
        factory=createFactory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
