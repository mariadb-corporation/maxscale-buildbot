from buildbot.plugins import schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="smart_remove_lock",
    builderNames=["smart_remove_lock"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="smart_remove_lock_force",
    builderNames=["smart_remove_lock"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_full_name(),
        properties.try_already_running(),
        properties.build_box(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
