import os
from buildbot.plugins import schedulers
from . import properties
from . import common
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build_new",
    builderNames=["build_new"],
    properties={
        "repository": constants.MAXSCALE_REPOSITORY,
        "branch": "develop",
        "box": constants.BOXES[0],
        "target": 'develop',
        "cmake_flags": constants.DEFAULT_CMAKE_FLAGS,
        "do_not_destroy_vm": 'no',
        "build_experimental": 'yes',
        "repo_path": os.environ['HOME'] + "/repository",
        "try_already_running": 'no',
        "run_upgrade_test": 'no',
        "old_target": "2.1.9",
        "ci_url": constants.CI_SERVER_URL
    }
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_new_force",
    buttonName="Start build manually",
    builderNames=["build_new"],
    codebases=[
        common.maxscale_codebase()
    ],
    properties=[
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
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
