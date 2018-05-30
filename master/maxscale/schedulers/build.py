import os
from buildbot.schedulers.forcesched import ChoiceStringParameter
from buildbot.schedulers.forcesched import CodebaseParameter
from buildbot.schedulers.forcesched import FixedParameter
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.forcesched import StringParameter
from buildbot.schedulers.triggerable import Triggerable
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = Triggerable(
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

MANUAL_SCHEDULER = ForceScheduler(
    name="build_force",
    label="Force build",
    builderNames=["build"],
    codebases=[
        CodebaseParameter(
            "",
            label="Main repository",
            branch=StringParameter(name="branch", default="develop"),
            revision=FixedParameter(name="revision", default=""),
            project=FixedParameter(name="project", default=""),
            repository=StringParameter(name="repository",
                                       default=constants.MAXSCALE_REPOSITORY),
        ),
    ],
    properties=[
        ChoiceStringParameter(
            name="box",
            label="Box",
            choices=constants.BOXES,
            default=constants.BOXES[0]),
        StringParameter(name="target", label="Target", size=50, default="develop"),
        StringParameter(name="cmake_flags", label="CMake flags", size=50,
                        default=constants.DEFAULT_CMAKE_FLAGS),
        ChoiceStringParameter(
            name="do_not_destroy_vm",
            label="Do not destroy vm",
            choices=['no', 'yes'],
            default='no'),
        ChoiceStringParameter(
            name="build_experimental",
            label="Build experimental",
            choices=["yes", "no"],
            default="yes"),
        StringParameter(name="repo_path", label="Repo path", size=50, default=os.environ['HOME'] + "/repository"),
        ChoiceStringParameter(
            name="try_already_running",
            label="Try already running",
            choices=["no", "yes"],
            default="no"),
        ChoiceStringParameter(
            name="run_upgrade_test",
            label="Run upgrade test",
            choices=["no", "yes"],
            default="no"),
        StringParameter(name="old_target", label="Old target", size=50, default="2.1.9"),
        StringParameter(name="ci_url", label="ci url", size=50,
                        default=constants.CI_SERVER_URL),

    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
