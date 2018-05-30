from buildbot.plugins import util, schedulers
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="cleanup",
    builderNames=["cleanup"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="cleanup_force",
    builderNames=["cleanup"],
    codebases=[
        util.CodebaseParameter(
            "",
            branch=util.FixedParameter(name="branch", default=""),
            revision=util.FixedParameter(name="revision", default=""),
            project=util.FixedParameter(name="project", default=""),
            repository=util.FixedParameter(name="repository",
                                           default=""),
        ),
    ],
    properties=[
        util.StringParameter(name="name", label="Name of this build", size=50, default="test01"),
        util.ChoiceStringParameter(
            name="do_not_destroy_vm",
            label="Do not destroy vm",
            choices=['no', 'yes'],
            default='no'),
        util.StringParameter(name="build_full_name", label="Build full name ('JOB_NAME-BUILD_ID')", size=50),
        util.ChoiceStringParameter(
            name="try_already_running",
            label="Try already running",
            choices=["no", "yes"],
            default="no"),
        util.ChoiceStringParameter(
            name="box",
            label="Box",
            choices=constants.BOXES,
            default=constants.BOXES[0]),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
