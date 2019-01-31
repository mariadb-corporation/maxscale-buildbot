from buildbot.plugins import schedulers
from . import properties

PERFORMACE_TEST_PROPERTIES = [
    properties.build_target(),
    properties.database_version(),
    properties.host("max-tst-01"),
    properties.maxscale_threads(),
    properties.sysbench_threads(),
    properties.perf_cnf_template(),
    properties.perf_port(),
    properties.perf_runtime(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_performance_test",
    buttonName="Force build",
    builderNames=["run_performance_test"],
    properties=PERFORMACE_TEST_PROPERTIES
)

#PERIODIC_SCHEDULER = schedulers.Periodic(
#   name="run_performance_test_half_hour",
#    builderNames=["run_performance_test"],
#    periodicBuildTimer=10*60,
#    properties=properties.extractDefaultValues(PERFORMACE_TEST_PROPERTIES)
#)

REPOSITORY_SCHEDULER = schedulers.Triggerable(
    name="run_performance_test_trigger",
    builderNames=["run_performance_test"],
)

#SCHEDULERS = [MANUAL_SCHEDULER, PERIODIC_SCHEDULER, REPOSITORY_SCHEDULER]
SCHEDULERS = [MANUAL_SCHEDULER, REPOSITORY_SCHEDULER]

