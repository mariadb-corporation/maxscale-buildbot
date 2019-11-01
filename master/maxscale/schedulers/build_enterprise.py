from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.build_box(),
    properties.build_target(),
    properties.ci_url(),
    properties.cmake_enterprise_flags(),
    properties.host(),
    properties.keep_virtual_machines(),
    properties.old_target(),
    properties.repository_path(),
    properties.run_upgrade_test(),
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build_enterprise",
    builderNames=["build_enterprise"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_enterprise_force",
    buttonName="Force build",
    builderNames=["build_enterprise"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_PROPERTIES
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
