from buildbot.plugins import schedulers
from . import properties
from maxscale.config import constants
from maxscale.config.branches_list_file import VALGRIND_BRANCHES_LIST
from maxscale.config.branches_list_file import NIGHTLY_BRANCHES_LIST
from maxscale.config.branches_list_file import DIFF_DISTRO_BRANCHES_LIST
from maxscale.builders.support.common import TargetInitOptions


BUILD_AND_TEST_PROPERTIES = [
    properties.build_name(),
    properties.appendTestRunId(),
    properties.build_target(),
    properties.build_experimental_features(),
    properties.build_box(),
    properties.backend_database(),
    properties.database_version(),
    properties.cmake_flags(),
    properties.keep_virtual_machines(),
    properties.test_set(),
    properties.ci_url(),
    properties.smoke_tests(),
    properties.big_number_of_vms(),
    properties.backend_use_ssl(),
    properties.host(),
    properties.use_valgrind(),
    properties.use_callgrind(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test",
    buttonName="Build and test",
    builderNames=["build_and_test"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_TEST_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]

DEFAULT_NIGHTLY_PROPERTIES = properties.extractDefaultValues(BUILD_AND_TEST_PROPERTIES)
del DEFAULT_NIGHTLY_PROPERTIES['host']  # We will set hosts manually for each scheduled build

# Add schedulers for every active branch to be built every night
# The list of branches is defined by constants.NIGHTLY_SCHEDS
# (see maxscale/config/constants.py)
BUILD_INTERVAL = 2
launchTime = 20
for branch_item in NIGHTLY_BRANCHES_LIST:
    nightlyProperties = DEFAULT_NIGHTLY_PROPERTIES.copy()
    nightlyProperties["name"] = "nightly_test_{}".format(branch_item["branch"])
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['buildHosts'] = ["bb-host"]
    nightlyProperties['test_set'] = branch_item["test_set"]
    nightlyProperties['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_{}_nightly".format(branch_item["branch"]),
        builderNames=["build_and_test_parall"],
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
    nightlyProperties = DEFAULT_NIGHTLY_PROPERTIES.copy()
    nightlyProperties["name"] = "valgrind_test_{}".format(branch_item["branch"])
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['buildHosts'] = ["bb-host"]
    nightlyProperties['use_valgrind'] = "yes"
    nightlyProperties['test_set'] = branch_item["test_set"]
    nightlyProperties['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_valgrind_{}_weekly".format(branch_item["branch"]),
        builderNames=["build_and_test_parall"],
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
    nightlyProperties = DEFAULT_NIGHTLY_PROPERTIES.copy()
    nightlyProperties["name"] = "diff_distro_test_{branch}_{box}".format(branch=branch_item["branch"],
                                                                         box=branch_item["box"])
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['buildHosts'] = ["bb-host"]
    nightlyProperties['use_valgrind'] = "no"
    nightlyProperties['test_set'] = branch_item["test_set"]
    nightlyProperties['box'] = branch_item["box"]
    nightlyProperties['cmake_flags'] = constants.DEFAULT_DAILY_TEST_CMAKE_FLAGS
    nightlyProperties["targetInitMode"] = TargetInitOptions.GENERATE

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_distros_{branch}_{box}_weekly".format(branch=branch_item["branch"],
                                                                   box=branch_item["box"]),
        builderNames=["build_and_test_parall"],
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
