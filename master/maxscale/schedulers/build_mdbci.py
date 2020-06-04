from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.host(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_mdbci_force",
    buttonName="Force build",
    builderNames=["build_mdbci"],
    codebases=properties.codebaseMdbciParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
