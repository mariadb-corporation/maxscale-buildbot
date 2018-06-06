from buildbot.plugins import util, schedulers
from maxscale.change_source.maxscale import check_branch_fn
from maxscale.config import constants

CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_simple_test_on_push",
    change_filter=util.ChangeFilter(project='maxscale', branch_fn=check_branch_fn),
    treeStableTimer=60,
    builderNames=["build_and_simple_test"],
    properties={
        "build_experimental": "yes",
        "product": "mariadb",
        "version": constants.DB_VERSIONS[0],
        "do_not_destroy_vm": "no",
        "ci_url": constants.CI_SERVER_URL,
        "backend_ssl": "no",
        "try_already_running": "yes",
        "maxscale_threads": "8",
        "sysbench_threads": "128"
    }
)


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_simple_test_force",
    label="Build and simple test",
    builderNames=["build_and_simple_test"],
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
            name="build_experimental",
            label="Build experimental",
            choices=["yes", "no"],
            default="yes"),
        util.ChoiceStringParameter(
            name="product",
            label="Product",
            choices=['mariadb', 'mysql'],
            default='mariadb'),
        util.ChoiceStringParameter(
            name="version",
            label="Version",
            choices=constants.DB_VERSIONS,
            default=constants.DB_VERSIONS[0]),
        util.ChoiceStringParameter(
            name="do_not_destroy_vm",
            label="Do not destroy vm",
            choices=['no', 'yes'],
            default='no'),
        util.StringParameter(name="test_set", label="Test set", size=50, default="-LE HEAVY"),
        util.StringParameter(name="ci_url", label="ci url", size=50,
                             default=constants.CI_SERVER_URL),
        util.ChoiceStringParameter(
            name="backend_ssl",
            label="Backend ssl",
            choices=["no", "yes"],
            default="no"),
        util.StringParameter(name="maxscale_threads", label="Maxscale threads", size=4, default="8"),
        util.StringParameter(name="sysbench_threads", label="Sysbench threads", size=4, default="128")
    ]
)

SCHEDULERS = [CHANGE_SOURCE_SCHEDULER, MANUAL_SCHEDULER]
