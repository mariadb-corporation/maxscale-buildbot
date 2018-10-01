from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

PERFORMACE_TEST_PROPERTIES = [
    properties.build_target(),
    properties.database_version(),
    properties.host1(),
    properties.maxscale_threads(),
    properties.sysbench_threads(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_performance_test",
    buttonName="Force build",
    builderNames=["run_performance_test"],
    properties=PERFORMACE_TEST_PROPERTIES
)

prop = properties.extractDefaultValues(PERFORMACE_TEST_PROPERTIES)
prop['target'] = "maxscale-2.2.15-release"

PERIODIC_SCHEDULER = schedulers.Periodic(
    name="run_performance_test_half_hour",
    builderNames=["run_performance_test"],
    periodicBuildTimer=10*60,
    properties=prop
)

REPOSITORY_SCHEDULER = schedulers.Triggerable(
    name="run_performance_test",
    builderNames=["run_performance_test"],
)

SCHEDULERS = [MANUAL_SCHEDULER, PERIODIC_SCHEDULER, REPOSITORY_SCHEDULER]
