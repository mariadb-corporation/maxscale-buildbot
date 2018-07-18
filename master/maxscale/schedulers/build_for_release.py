from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

BUILD_FOR_RELEASE_PROPERTIES = [
    properties.versionNumber(),
    properties.build_experimental_features(),
    properties.old_target(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_for_release",
    builderNames=["build_for_release"],
    buttonName="Build for release",
    codebases=properties.codebaseParameter(),
    properties=BUILD_FOR_RELEASE_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
