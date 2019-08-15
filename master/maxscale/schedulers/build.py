from buildbot.plugins import schedulers
from . import properties

BUILD_PROPERTIES = [
    properties.build_box(),
    properties.build_experimental_features(),
    properties.build_target(),
    properties.ci_url(),
    properties.cmake_flags(),
    properties.host(),
    properties.keep_virtual_machines(),
    properties.old_target(),
    properties.repository_path(),
    properties.run_upgrade_test(),
    properties.try_already_running(),
]

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
