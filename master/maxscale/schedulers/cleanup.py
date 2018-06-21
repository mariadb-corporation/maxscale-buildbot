from buildbot.plugins import schedulers
from . import common
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="cleanup",
    builderNames=["cleanup"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="cleanup_force",
    buttonName="Cleanup",
    builderNames=["cleanup"],
    codebases=[
        common.maxscale_codebase()
    ],
    properties=[
        properties.build_name(),
        properties.keep_virtual_machines(),
        properties.build_full_name(),
        properties.try_already_running(),
        properties.build_box(),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
