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
    "ci_url",
    "smoke",
    "big",
    "host",
    "owners",
]


def create_factory():
    factory = BuildFactory()
    factory.addSteps(common.initTargetProperty())
    factory.addSteps(common.initNameProperty())
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

    if util.Property("host") == "bb-host":
        testHost = "max-gcloud"
    else:
        testHost = util.Property("host")

    factory.addStep(steps.Trigger(
        name="Call the 'run_test' scheduler",
        schedulerNames=['run_test'],
        waitForFinish=False,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            'test_branch': util.Property('branch'),
            "test_set": '-L set01',
            "use_valgrind": util.Property("use_valgrind"),
            "use_callgrind": util.Property("use_callgrind"),
            "backend_ssl": util.Property("backend_ssl"),
            "host": testHost,
            "name":  util.Property("backend_ssl") + '-01',
        }
    ))
   factory.addStep(steps.Trigger(
        name="Call the 'run_test' scheduler",
        schedulerNames=['run_test'],
        waitForFinish=False,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            'test_branch': util.Property('branch'),
            "test_set": '-L set02',
            "use_valgrind": util.Property("use_valgrind"),
            "use_callgrind": util.Property("use_callgrind"),
            "backend_ssl": util.Property("backend_ssl"),
            "host": testHost,
            "name":  util.Property("backend_ssl") + '-02',
        }
    ))

   factory.addStep(steps.Trigger(
        name="Call the 'run_test' scheduler",
        schedulerNames=['run_test'],
        waitForFinish=False,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            'test_branch': util.Property('branch'),
            "test_set": '-L set03',
            "use_valgrind": util.Property("use_valgrind"),
            "use_callgrind": util.Property("use_callgrind"),
            "backend_ssl": util.Property("backend_ssl"),
            "host": testHost,
            "name":  util.Property("backend_ssl") + '-03',
        }
    ))


    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_parall",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
