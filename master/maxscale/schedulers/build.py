import os
from buildbot.plugins import util, schedulers
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="build",
    builderNames=["build"],
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
    name="build_force",
    label="Force build",
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
        ),
    ],
    properties=[
        util.ChoiceStringParameter(
            name="box",
            label="Box",
            choices=constants.BOXES,
            default=constants.BOXES[0]),
        util.StringParameter(name="target", label="Target", size=50, default="develop"),
        util.StringParameter(name="cmake_flags", label="CMake flags", size=50,
                             default=constants.DEFAULT_CMAKE_FLAGS),
        util.ChoiceStringParameter(
            name="do_not_destroy_vm",
            label="Do not destroy vm",
            choices=['no', 'yes'],
            default='no'),
        util.ChoiceStringParameter(
            name="build_experimental",
            label="Build experimental",
            choices=["yes", "no"],
            default="yes"),
        util.StringParameter(name="repo_path", label="Repo path", size=50, default=os.environ['HOME'] + "/repository"),
        util.ChoiceStringParameter(
            name="try_already_running",
            label="Try already running",
            choices=["no", "yes"],
            default="no"),
        util.ChoiceStringParameter(
            name="run_upgrade_test",
            label="Run upgrade test",
            choices=["no", "yes"],
            default="no"),
        util.StringParameter(name="old_target", label="Old target", size=50, default="2.1.9"),
        util.StringParameter(name="ci_url", label="ci url", size=50,
                             default=constants.CI_SERVER_URL),

    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
