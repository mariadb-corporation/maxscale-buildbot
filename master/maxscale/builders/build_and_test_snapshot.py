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
]


def createFactory():
    factory = BuildFactory()
    factory.addSteps(common.setMissingTarget())
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
            'virtual_builder_name': 'Build for ubuntu_xenial_libvirt',
        }
    ))
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
            "test_set": util.Property("test_set"),
            "backend_ssl": util.Property("backend_ssl"),
            'virtual_builder_name': 'Run functional tests',
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
