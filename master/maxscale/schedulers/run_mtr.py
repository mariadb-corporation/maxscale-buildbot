from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.build_target(),
    properties.image(),
    properties.mtrParam();
    properties.host(),
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="run_mtr",
    builderNames=["run_mtr"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_mtr_force",
    buttonName="Force build",
    builderNames=["run_mtr"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
