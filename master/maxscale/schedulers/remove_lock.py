from buildbot.plugins import util, schedulers
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="remove_lock",
    builderNames=["remove_lock"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="remove_lock_force",
    builderNames=["remove_lock"],
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
