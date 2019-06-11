from buildbot.plugins import schedulers
from maxscale.config import constants
from . import common
from . import properties

from maxscale.builders.run_test import NEEDED_PROPERTIES

RUN_TEST_PROPERTIES = properties.setSchedulerProperties(NEEDED_PROPERTIES, [
    properties.build_name(),
    properties.host(),
])

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="run_test",
    builderNames=["run_test"],
    codebases=constants.MAXSCALE_CODEBASE,
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_test_force",
    buttonName="Run tests",
    builderNames=["run_test"],
    codebases=properties.codebaseParameter(),
    properties=RUN_TEST_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
