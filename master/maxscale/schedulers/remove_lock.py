from buildbot.plugins import schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="remove_lock",
    builderNames=["remove_lock"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="remove_lock_force",
    buttonName="Remove lock",
    builderNames=["remove_lock"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.try_already_running(),
        properties.build_box(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
