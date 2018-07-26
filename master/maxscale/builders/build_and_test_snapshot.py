import os
import datetime

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.process.results import SKIPPED
from maxscale import workers

COMMON_BUILD_AND_TEST_SNAPSHOT_PROPERTIES = [
    "branch",
    "repository",
    "cmake_flags",
    "build_experimental",
    "product",
    "version",
    "ci_url",
]


@util.renderer
def formatStartTime(properties):
    return datetime.datetime.now().strftime("%b%d-%H:%M:%S")


def createFactory():
    factory = BuildFactory()
    factory.addStep(steps.SetProperty(
        name=util.Interpolate("Set 'target' property"),
        property="target",
        value=util.Interpolate("%(prop:branch)s-buildbot-%(kw:startTime)s",
                               startTime=formatStartTime),
        doStepIf=lambda step: step.build.getProperty('target') is None,
        hideStepIf=lambda results, s: results == SKIPPED
    ))
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
            "box": util.Property("box"),
            'try_already_running': 'yes',
            "target": util.Property("target")
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
            "backend_ssl": util.Property("backend_ssl")
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
