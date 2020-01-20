from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.build_target(),
    properties.buildType(),
    properties.host(),
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build_and_test_es_all",
    builderNames=["build_and_test_es_all"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test_es_all_force",
    buttonName="Build and test",
    builderNames=["build_and_test_es_all"],
    codebases=properties.codebaseESParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
