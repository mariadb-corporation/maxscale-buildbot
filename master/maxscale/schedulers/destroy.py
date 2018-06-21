from buildbot.plugins import schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="destroy",
    builderNames=["destroy"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="destroy_force",
    builderNames=["destroy"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_name(),
        properties.keep_virtual_machines(),
        properties.try_already_running(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
