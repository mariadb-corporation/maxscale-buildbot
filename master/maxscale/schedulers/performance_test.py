from buildbot.plugins import util, schedulers
from maxscale.config import constants


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="performance_test",
    builderNames=["performance_test"],
    properties={
        "repository": constants.MAXSCALE_REPOSITORY,
        "branch": "develop",
        "target": "develop",
        "maxscale_threads": "8",
        "sysbench_threads": "128"
    }
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="performance_test_force",
    label="Performance test",
    builderNames=["performance_test"],
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
        util.StringParameter(name="target", label="Target", size=50, default="develop"),
        util.ChoiceStringParameter(
            name="version",
            label="Version",
            choices=constants.DB_VERSIONS,
            default=constants.DB_VERSIONS[0]),
        util.StringParameter(name="maxscale_threads", label="Maxscale threads", size=4, default="8"),
        util.StringParameter(name="sysbench_threads", label="Sysbench threads", size=4, default="128")
    ]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER, MANUAL_SCHEDULER]
