import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from .support import common

COMMON_PROPERTIES = [
    "name",
    "repository",
    "branch",
    "target",
    "build_experimental",
    "box",
    "product",
    "version",
    "cmake_flags",
    "do_not_destroy_vm",
    "ci_url",
    "smoke",
    "big",
    "host",
    "owners",
]


def createFactory():
    factory = BuildFactory()
    factory.addSteps(common.initTargetProperty())
    factory.addSteps(common.initNameProperty())
    factory.addStep(common.determineBuildId())
    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            'virtual_builder_name': util.Interpolate('Build for %(prop:box)s'),
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'run_test' scheduler",
        schedulerNames=['run_test'],
        waitForFinish=True,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            "appendTestRunId": util.Property("appendTestRunId"),
            "backend_ssl": util.Property("backend_ssl"),
            "buildId": util.Property("buildId"),
            "host": util.Property("host"),
            "test_branch": util.Property("branch"),
            "test_set": common.renderTestSet,
            "use_callgrind": util.Property("use_callgrind"),
            "use_valgrind": util.Property("use_valgrind"),
        }
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=createFactory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
