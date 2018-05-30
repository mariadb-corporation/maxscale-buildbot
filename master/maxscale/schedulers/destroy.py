from buildbot.plugins import util, schedulers


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="destroy",
    builderNames=["destroy"]
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="destroy_force",
    builderNames=["destroy"],
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
        util.ChoiceStringParameter(
            name="try_already_running",
            label="Try already running",
            choices=["no", "yes"],
            default="no"),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
