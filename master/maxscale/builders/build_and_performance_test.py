import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants

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
    "test_set",
    "ci_url",
    "smoke",
    "big",
    "host",
    "owners",
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
            'box': 'ubuntu_bionic_libvirt',
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'run_performance_test' scheduler",
        schedulerNames=['run_performace_test'],
        waitForFinish=True,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            'test_branch': util.Property('branch'),
            'host' : 'max-tst-01',
        }
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_performance_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
