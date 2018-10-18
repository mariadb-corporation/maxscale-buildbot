from buildbot.plugins import schedulers, util
from . import properties
from maxscale.config import constants


BUILD_AND_PERFORMANCE_TEST_PROPERTIES = [
    properties.backend_database(),
    properties.database_version(),
    properties.cmake_flags(),
    properties.host1(),
    properties.maxscale_threads(),
    properties.sysbench_threads(),
    properties.build_box('ubuntu_bionic_libvirt'),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_performance_test",
    label="Build and performance test",
    builderNames=["build_and_performance_test"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_PERFORMANCE_TEST_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]

# Add schedulers for every active branch to be built every night
# The list of branches is defined by constants.NIGHTLY_SCHEDS
# (see maxscale/config/constants.py)
BUILD_INTERVAL = 1
launchTime = 18
for branch in constants.NIGHTLY_SCHEDS:
    nightlyProperties = properties.extractDefaultValues(BUILD_AND_PERFORMANCE_TEST_PROPERTIES)
    nightlyProperties["name"] = "nightly_test_{}".format(branch)
    nightlyProperties['owners'] = constants.NIGHTLY_MAIL_LIST
    del nightlyProperties["target"]

    nightlyScheduler = schedulers.Nightly(
        name="build_and_performance_test_{}_nightly".format(branch),
        builderNames=["build_and_test"],
        hour=launchTime % 24, minute=1,
        codebases={"": {
            "branch": branch,
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
    launchTime += BUILD_INTERVAL
