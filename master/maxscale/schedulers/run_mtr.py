from buildbot.plugins import schedulers, util
from . import properties

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="mtr_force",
    buttonName="MTR",
    builderNames=["run_mtr"],
    codebases=[util.CodebaseParameter(codebase='', hide=True)],
    properties=[
        properties.build_name(),
        properties.host(),
    ]
)

SCHEDULERS = [MANUAL_SCHEDULER]
