from buildbot.plugins import schedulers
from maxscale.builders.support.common import setSchedulerProperties
from maxscale.config import constants
from . import properties

from maxscale.builders.build import NEEDED_PROPERTIES

BUILD_PROPERTIES = setSchedulerProperties(NEEDED_PROPERTIES, [
    properties.repository_path(),
    properties.host(),
])

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build",
    builderNames=["build"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_force",
    buttonName="Force build",
    builderNames=["build"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
