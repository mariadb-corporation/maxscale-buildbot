from buildbot.plugins import schedulers, util
from . import properties
from maxscale.change_source.maxscale import get_test_set_by_branch
from maxscale.config import constants


BUILD_AND_TEST_PROPERTIES = [
    properties.build_name(),
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
]

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
for branch in constants.NIGHTLY_SCHEDS:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_TEST_PROPERTIES)
    nightlyProperties["name"] = "nightly_test_{}".format(branch)
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    nightlyProperties['host'] = "max-tst-02"
    nightlyProperties['test_set'] = get_test_set_by_branch(branch)
    del nightlyProperties["target"]

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_{}_nightly".format(branch),
        builderNames=["build_and_test"],
        hour=launchTime % 24, minute=0,
        codebases={"": {
            "branch": branch,
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
    launchTime += BUILD_INTERVAL
