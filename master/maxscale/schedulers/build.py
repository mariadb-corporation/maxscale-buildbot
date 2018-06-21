import os
from buildbot.plugins import util, schedulers
from maxscale.config import constants
from . import properties


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build",
    builderNames=["build"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_force",
    buttonName="Force build",
    builderNames=["build"],
    codebases=[
        util.CodebaseParameter(
            "",
            label="Main repository",
            branch=util.StringParameter(name="branch", default="develop"),
            revision=util.FixedParameter(name="revision", default=""),
            project=util.FixedParameter(name="project", default=""),
            repository=util.StringParameter(name="repository",
                                            default=constants.MAXSCALE_REPOSITORY),
        )
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
