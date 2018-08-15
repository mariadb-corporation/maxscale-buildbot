from buildbot.plugins import schedulers, util
from . import properties

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="destroy_force",
    buttonName="Destroy",
    builderNames=["destroy"],
    codebases=[util.CodebaseParameter(codebase='', hide=True)],
    properties=[
        properties.build_name(),
        properties.host(),
    ]
)

SCHEDULERS = [MANUAL_SCHEDULER]
