from buildbot.plugins import util, schedulers
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

BUILD_AND_TEST_SNAPSHOT_PROPERTIES = [
    properties.build_target(),
    properties.test_set(),
    properties.host(),
] + COMMON_PROPERTIES

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test_snapshot_force",
    buttonName="Build and test snapshot",
    builderNames=["build_and_test_snapshot"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_TEST_SNAPSHOT_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
