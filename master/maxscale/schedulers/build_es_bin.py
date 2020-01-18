from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.build_target(),
    properties.image(),
    properties.buildType(),
    properties.host(),
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build_es_bin",
    builderNames=["build_es_bin"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_es_bin_force",
    buttonName="Force build",
    builderNames=["build_es_bin"],
    codebases=properties.codebaseESParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
