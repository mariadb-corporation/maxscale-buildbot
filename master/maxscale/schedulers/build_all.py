from buildbot.plugins import schedulers
from . import properties
from . import common


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_all",
    builderNames=["build_all"],
    buttonName="Build all",
    codebases=[
        common.maxscale_codebase()
    ],
    properties=[
        properties.buildBoxCheckboxContainer(),
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
)


SCHEDULERS = [MANUAL_SCHEDULER]
