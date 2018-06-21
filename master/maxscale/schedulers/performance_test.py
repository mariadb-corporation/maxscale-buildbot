from buildbot.plugins import schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="performance_test",
    builderNames=["performance_test"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="performance_test_force",
    buttonName="Performance test",
    builderNames=["performance_test"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_target(),
        properties.database_version(),
        properties.maxscale_threads(),
        properties.sysbench_threads(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
