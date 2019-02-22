import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common

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
            "test_set": common.renderTestSet,
            "backend_ssl": util.Property("backend_ssl"),
            "use_valgrind": util.Property("use_valgrind"),
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_snapshot",
        workernames=workers.workerNames(),
        nextWorker=common.assignBestHost(['max-tst-02', 'max-tst-03']),
        nextBuild=common.assignBuildRequest,
        factory=createFactory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
