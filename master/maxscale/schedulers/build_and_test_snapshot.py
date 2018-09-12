from buildbot.plugins import util, schedulers
from maxscale.change_source.maxscale import check_branch_fn
from . import common
from . import properties
from maxscale.config import constants

COMMON_PROPERTIES = [
    properties.build_box(),
    properties.cmake_flags(),
    properties.build_experimental_features(),
    properties.backend_database(),
    properties.database_version(),
    properties.ci_url(),
    properties.backend_use_ssl(),
]

BUILD_AND_TEST_SNAPSHOT_PROPERTIES = [
    properties.build_target(),
    properties.test_set(),
    properties.host(),
] + COMMON_PROPERTIES

DEFAULT_PROPERTIES = properties.extractDefaultValues(COMMON_PROPERTIES)

CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_test_snapshot_on_push",
    change_filter=util.ChangeFilter(project='maxscale', branch_fn=check_branch_fn),
    treeStableTimer=60,
    codebases=constants.MAXSCALE_CODEBASE,
    builderNames=["build_and_test_snapshot"],
    properties=DEFAULT_PROPERTIES
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test_snapshot_force",
    buttonName="Build and test snapshot",
    builderNames=["build_and_test_snapshot"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_TEST_SNAPSHOT_PROPERTIES
)

SCHEDULERS = [CHANGE_SOURCE_SCHEDULER, MANUAL_SCHEDULER]
