from buildbot.plugins import schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="remove_lock_snapshot",
    builderNames=["remove_lock_snapshot"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="remove_lock_snapshot_force",
    buttonName="Remove snapshot lock",
    builderNames=["remove_lock_snapshot"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_name(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
