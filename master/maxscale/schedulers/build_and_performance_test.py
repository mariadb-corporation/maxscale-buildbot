from buildbot.plugins import schedulers, util
from . import properties
from . import common
from maxscale.config import constants
from maxscale.change_source.maxscale import check_branch_fn_perf
from maxscale.builders.support.common import TargetInitOptions


BUILD_AND_PERFORMANCE_TEST_PROPERTIES = [
    properties.build_target(),
    properties.backend_database(),
    properties.database_version(),
    properties.cmake_flags(constants.DEFAULT_RELEASE_CMAKE_FLAGS),
    properties.host("max-tst-01"),
    properties.maxscale_threads(),
    properties.sysbench_threads(),
    properties.perf_cnf_template(),
    properties.perf_port(),
    properties.perf_runtime(),
    properties.build_box('ubuntu_bionic_libvirt'),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_performance_test",
    label="Build and performance test",
    builderNames=["build_and_performance_test"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_PERFORMANCE_TEST_PROPERTIES
)

ON_PUSH_PROPERTIES = properties.extractDefaultValues(BUILD_AND_PERFORMANCE_TEST_PROPERTIES)
ON_PUSH_PROPERTIES["targetInitMode"] = TargetInitOptions.SET_FROM_BRANCH

CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_performance_test_on_push",
    change_filter=util.ChangeFilter(project='maxscale', branch_fn=check_branch_fn_perf),
    treeStableTimer=60,
    codebases=constants.MAXSCALE_CODEBASE,
    builderNames=["build_and_performance_test"],
    properties=ON_PUSH_PROPERTIES
)


SCHEDULERS = [MANUAL_SCHEDULER, CHANGE_SOURCE_SCHEDULER]

# Add schedulers for every active branch to be built every night
# The list of branches is defined by constants.NIGHTLY_SCHEDS
# (see maxscale/config/constants.py)
BUILD_INTERVAL = 1
launchTime = 18
for branch in constants.NIGHTLY_SCHEDS:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_PERFORMANCE_TEST_PROPERTIES)
    nightlyProperties["name"] = "nightly_test_{}".format(branch)
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_performance_test_{}_nightly".format(branch),
        builderNames=["build_and_performance_test"],
        hour=launchTime % 24, minute=0,
        codebases={"": {
            "branch": branch,
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
    launchTime += BUILD_INTERVAL
