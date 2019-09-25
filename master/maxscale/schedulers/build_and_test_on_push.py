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
    properties.use_valgrind(),
]

DEFAULT_PROPERTIES = properties.extractDefaultValues(COMMON_PROPERTIES)
DEFAULT_PROPERTIES['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
DEFAULT_PROPERTIES["targetInitMode"] = TargetInitOptions.GENERATE
DEFAULT_PROPERTIES['name'] = "on_push_test"

CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_test_on_push",
    change_filter=util.ChangeFilter(project='maxscale', branch_fn=check_branch_fn),
    treeStableTimer=60,
    codebases=constants.MAXSCALE_CODEBASE,
    builderNames=["build_and_test"],
    properties=DEFAULT_PROPERTIES
)

SCHEDULERS = [CHANGE_SOURCE_SCHEDULER]
