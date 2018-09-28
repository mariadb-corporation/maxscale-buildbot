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


PERIODIC_SCHEDULER = schedulers.Periodic(
    name="run_performance_test_half_hour",
    builderNames=["run_performance_test"],
    periodicBuildTimer=30*60,
    properties=PERFORMACE_TEST_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER, PERIODIC_SCHEDULER]
