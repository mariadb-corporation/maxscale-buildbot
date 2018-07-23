import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers

COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES = [
    "branch",
    "repository",
    "box",
    "target",
    "cmake_flags",
    "build_experimental",
    "product",
    "version",
    "ci_url",
]


def createFactory():
    factory = BuildFactory()
    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler. Build Ubuntu",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES,
        set_properties={
            'box': 'ubuntu_xenial_libvirt',
            'try_already_running': 'yes',
            'target': util.Interpolate("%(prop:target)s-perf"),
        }
    ))
    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler. Build CentOS",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES,
        set_properties={
            'try_already_running': 'yes'
        }
    ))
    factory.addStep(steps.Trigger(
        name="Call the 'run_test_snapshot' scheduler. Run functional tests",
        schedulerNames=['run_test_snapshot'],
        waitForFinish=True,
        copy_properties=COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES + ["test_set", "backend_ssl"],
        set_properties={
            "test_branch": util.Property("branch")
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_snapshot",
        workernames=workers.workerNames(),
        factory=createFactory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
