from buildbot.plugins import schedulers, util
from . import properties
from maxscale.change_source.maxscale import get_test_set_by_branch
from maxscale.config import constants
from maxscale.config.branches_list_file import VALGRIND_BRANCHES_LIST
from maxscale.config.branches_list_file import NIGHTLY_BRANCHES_LIST
from maxscale.config.branches_list_file import DIFF_DISTRO_BRANCHES_LIST
from maxscale.builders.support.common import TargetInitOptions

from maxscale.builders.build_and_test import REQUIRED_PROPERTIES

BUILD_AND_TEST_PROPERTIES = properties.setSchedulerProperties(REQUIRED_PROPERTIES, [
    properties.repository_path(),
    properties.host(),
    properties.build_name()
])

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test",
    label="Build and test",
    builderNames=["build_and_test"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_TEST_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]

# Add schedulers for every active branch to be built every night
# The list of branches is defined by constants.NIGHTLY_SCHEDS
# (see maxscale/config/constants.py)
BUILD_INTERVAL = 3
launchTime = 20
for branch_item in NIGHTLY_BRANCHES_LIST:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_TEST_PROPERTIES)
    nightlyProperties["name"] = "nightly_test_{}".format(branch_item["branch"])
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['host'] = "max-tst-02"
    nightlyProperties['test_set'] = branch_item["test_set"]
    nightlyProperties['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_{}_nightly".format(branch_item["branch"]),
        builderNames=["build_and_test"],
        hour=launchTime % 24, minute=0,
        codebases={"": {
            "branch": branch_item["branch"],
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
    launchTime += BUILD_INTERVAL

# Add scheduler for test with Valgrind
BUILD_INTERVAL = 8
launchTime = 8
for branch_item in VALGRIND_BRANCHES_LIST:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_TEST_PROPERTIES)
    nightlyProperties["name"] = "valgrind_test_{}".format(branch_item["branch"])
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['host'] = "max-tst-02"
    nightlyProperties['use_valgrind'] = "yes"
    nightlyProperties['test_set'] = branch_item["test_set"]
    nightlyProperties['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_valgrind_{}_weekly".format(branch_item["branch"]),
        builderNames=["build_and_test"],
        hour=launchTime % 24, minute=0,
        dayOfWeek=5,
        codebases={"": {
            "branch": branch_item["branch"],
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
    launchTime += BUILD_INTERVAL

# Add scheduler for test with different distros
BUILD_INTERVAL = 8
launchTime = 8
for branch_item in DIFF_DISTRO_BRANCHES_LIST:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_TEST_PROPERTIES)
    nightlyProperties["name"] = "diff_distro_test_{branch}_{box}".format(branch=branch_item["branch"], box=branch_item["box"])
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['host'] = "max-tst-02"
    nightlyProperties['use_valgrind'] = "no"
    nightlyProperties['test_set'] = branch_item["test_set"]
    nightlyProperties['box'] = branch_item["box"]
    nightlyProperties['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_distros_{branch}_{box}_weekly".format(branch=branch_item["branch"], box=branch_item["box"]),
        builderNames=["build_and_test"],
        hour=launchTime % 24, minute=0,
        dayOfWeek=6,
        codebases={"": {
            "branch": branch_item["branch"],
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
    launchTime += BUILD_INTERVAL
