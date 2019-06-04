import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants

from .run_test import NEEDED_PROPERTIES as RUN_TEST_NEEDED_PROPERTIES
from .build import NEEDED_PROPERTIES as BUILD_TEST_NEEDED_PROPERTIES

NEEDED_PROPERTIES = list(set(RUN_TEST_NEEDED_PROPERTIES + BUILD_TEST_NEEDED_PROPERTIES))


def create_factory():
    factory = BuildFactory()
    factory.addSteps(common.initTargetProperty())
    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=BUILD_TEST_NEEDED_PROPERTIES,
        set_properties={
            'virtual_builder_name': util.Interpolate('Build for %(prop:box)s'),
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'run_test' scheduler",
        schedulerNames=['run_test'],
        waitForFinish=True,
        copy_properties=RUN_TEST_NEEDED_PROPERTIES,
        set_properties={
            "test_set": common.renderTestSet
        }
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
