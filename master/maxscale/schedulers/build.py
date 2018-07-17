from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

BUILD_PROPERTIES = [
    properties.build_box(),
    properties.build_target(),
    properties.cmake_flags(),
    properties.keep_virtual_machines(),
    properties.build_experimental_features(),
    properties.repository_path(),
    properties.try_already_running(),
    properties.run_upgrade_test(),
    properties.old_target(),
    properties.ci_url()
]

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build",
    builderNames=["build"],
    codebases=constants.MAXSCALE_CODEBASE,
    properties=properties.extractDefaultValues(BUILD_PROPERTIES)
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_force",
    buttonName="Force build",
    builderNames=["build"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_PROPERTIES
)

BUILD_ALL_TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
   name="build_all_subtask",
   builderNames=["build"]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER, BUILD_ALL_TRIGGERABLE_SCHEDULER]
