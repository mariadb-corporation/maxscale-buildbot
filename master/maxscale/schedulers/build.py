from buildbot.plugins import schedulers
from . import properties
from . import common

buildProperties = [
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

triggerableScheduler = schedulers.Triggerable(
    name="build",
    builderNames=["build"],
    codebases=[
        common.maxscale_codebase()
    ],
    properties=properties.extractDefaultProperties(buildProperties)
)

manualScheduler = schedulers.ForceScheduler(
    name="build_force",
    buttonName="Force build",
    builderNames=["build"],
    codebases=[
        common.maxscale_codebase()
    ],
    properties=buildProperties
)

SCHEDULERS = [triggerableScheduler, manualScheduler]
