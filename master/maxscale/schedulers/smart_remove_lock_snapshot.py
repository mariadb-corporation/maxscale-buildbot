from buildbot.plugins import util, schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="smart_remove_lock_snapshot",
    builderNames=["smart_remove_lock_snapshot"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="smart_remove_lock_snapshot_force",
    builderNames=["smart_remove_lock_snapshot"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_name(),
        properties.build_full_name(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
