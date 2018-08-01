import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common

COMMON_PROPERTIES = [
    "name",
    "repository",
    "branch",
    "target",
    "build_experimental",
    "box",
    "product",
    "version",
    "cmake_flags"
    "do_not_destroy_vm",
    "test_set",
    "ci_url",
    "smoke",
    "big"
]


def create_factory():
    factory = BuildFactory()
    factory.addSteps(common.setMissingTarget())
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
            'test_branch': util.Property('branch'),
            'virtual_builder_name': util.Interpolate('Run tests'),
        }
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test",
        workernames=workers.workerNames(),
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
