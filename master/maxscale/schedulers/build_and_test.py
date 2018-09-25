from buildbot.plugins import schedulers, util
from . import properties
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
    properties.host("max-tst-01"),
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
for branch in constants.NIGHTLY_SCHEDS:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_TEST_PROPERTIES)
    nightlyProperties["name"] = "nightly_test_{}".format(branch)
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    del nightlyProperties["target"]

    nightlyScheduler = schedulers.Nightly(
        name="build_and_test_{}_nightly".format(branch),
        builderNames=["build_and_test"],
        hour=23, minute=00,
        codebases={"": {
            "branch": branch,
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
