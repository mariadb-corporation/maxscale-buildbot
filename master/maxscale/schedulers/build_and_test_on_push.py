from buildbot.plugins import util, schedulers
from maxscale.change_source.maxscale import check_branch_fn
from maxscale.builders.support.common import TargetInitOptions, NameInitOptions
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
    properties.appendTestRunId(),
]

DEFAULT_PROPERTIES = properties.extractDefaultValues(COMMON_PROPERTIES)
DEFAULT_PROPERTIES['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
DEFAULT_PROPERTIES["targetInitMode"] = TargetInitOptions.GENERATE
DEFAULT_PROPERTIES["nameInitMode"] = NameInitOptions.GENERATE
DEFAULT_PROPERTIES["buildHosts"] = ["max-gcloud-01", "max-gcloud-02"]

CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_test_on_push",
    change_filter=util.ChangeFilter(project=constants.MAXSCALE_PRODUCT, branch_fn=check_branch_fn),
    treeStableTimer=5,
    codebases=constants.MAXSCALE_CODEBASE,
    builderNames=["build_and_test_parall"],
    properties=DEFAULT_PROPERTIES
)

SCHEDULERS = [CHANGE_SOURCE_SCHEDULER]
