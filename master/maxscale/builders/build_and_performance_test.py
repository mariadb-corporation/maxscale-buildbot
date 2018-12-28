import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants

COMMON_PROPERTIES = [
    "repository",
    "branch",
    "target",
    "build_experimental",
    "box",
    "product",
    "version",
    "cmake_flags",
    "do_not_destroy_vm",
    "host",
    "owners",
    "maxscale_threads",
    "sysbench_threads",
    "perf_runtime",
    "perf_port",
    "perf_cnf_template"
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
            'try_already_running': 'yes',
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'run_performance_test' scheduler",
        schedulerNames=['run_performance_test_trigger'],
        waitForFinish=True,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            'test_branch': util.Property('branch'),
            'host': 'max-tst-01',
        }
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_performance_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
