from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

BUILD_PROPERTIES = [
    properties.repository_path(),
    properties.host(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_force",
    buttonName="Force build",
    builderNames=["build_mdbci"],
    codebases=properties.codebaseMdbciParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
