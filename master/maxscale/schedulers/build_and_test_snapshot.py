from buildbot.plugins import util, schedulers
from maxscale.change_source.maxscale import check_branch_fn
from . import common
from . import properties
from maxscale.config import constants


CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_test_snapshot_on_push",
    change_filter=util.ChangeFilter(project='maxscale', branch_fn=check_branch_fn),
    treeStableTimer=60,
    codebases={
        "codebase1": {
            "branch": "develop",
            "repository": constants.MAXSCALE_REPOSITORY
        }
    },
    builderNames=["build_and_test_snapshot"],
)


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test_snapshot_force",
    buttonName="Build and simple test",
    builderNames=["build_and_test_snapshot"],
    codebases=[
        common.maxscale_codebase()
    ],
    properties=[
        properties.build_target(),
        properties.build_experimental_features(),
        properties.backend_database(),
        properties.database_version(),
        properties.test_set(),
        properties.ci_url(),
        properties.backend_use_ssl(),
    ]
)

SCHEDULERS = [CHANGE_SOURCE_SCHEDULER, MANUAL_SCHEDULER]
