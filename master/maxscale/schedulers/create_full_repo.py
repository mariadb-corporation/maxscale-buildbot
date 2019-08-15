from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

BUILD_PROPERTIES = [
    properties.build_box(),
    properties.build_target(),
    properties.ci_url(),
    properties.host(),
    properties.keep_virtual_machines(),
    properties.repository_path(),
    properties.major_ver()
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="create_full_repo",
    builderNames=["create_full_repo"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="create_full_repo_force",
    buttonName="Force build",
    builderNames=["create_full_repo"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
