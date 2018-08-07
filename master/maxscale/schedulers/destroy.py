from buildbot.plugins import schedulers
from . import properties

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="destroy_force",
    builderNames=["destroy"],
    codebases=properties.codebaseParameter(),
    properties=[
        properties.build_name(),
        properties.keep_virtual_machines(),
        properties.try_already_running(),
    ]
)

SCHEDULERS = [MANUAL_SCHEDULER]
