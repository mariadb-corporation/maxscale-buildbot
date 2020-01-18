from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.build_target(),
    properties.host(),
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build_es_star",
    builderNames=["build_es_star"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_es_start_force",
    buttonName="Force build",
    builderNames=["build_es_star"],
    codebases=properties.codebaseESParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
