from buildbot.plugins import util, schedulers


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="smart_remove_lock_snapshot",
    builderNames=["smart_remove_lock_snapshot"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="smart_remove_lock_snapshot_force",
    builderNames=["smart_remove_lock_snapshot"],
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
        util.StringParameter(name="name",
                             label="Name of this build",
                             default="test01",
                             size=50),
        util.StringParameter(name="build_full_name",
                             label="Build full name ('JOB_NAME-BUILD_ID')",
                             size=50),
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]