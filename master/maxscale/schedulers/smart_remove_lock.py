from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.triggerable import Triggerable
from buildbot.plugins import util
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = Triggerable(
    name="smart_remove_lock",
    builderNames=["smart_remove_lock"],
)

MANUAL_SCHEDULER = ForceScheduler(
    name="smart_remove_lock_force",
    builderNames=["smart_remove_lock"],
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
