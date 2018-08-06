from buildbot.plugins import util, schedulers
from maxscale.change_source.maxscale import check_branch_fn
from . import common
from . import properties
from maxscale.config import constants

BUILD_AND_TEST_SNAPSHOT_PROPERTIES = [
    properties.build_box(),
    properties.build_target(),
    properties.cmake_flags(),
    properties.build_experimental_features(),
    properties.backend_database(),
    properties.database_version(),
    properties.test_set(),
    properties.ci_url(),
    properties.backend_use_ssl(),
    properties.host(),
]

DEFAULT_PROPERTIES = \
    properties.extractDefaultValues(BUILD_AND_TEST_SNAPSHOT_PROPERTIES)
DEFAULT_PROPERTIES["host"] = "max-tst-02.mariadb.com"
del DEFAULT_PROPERTIES["target"]

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
