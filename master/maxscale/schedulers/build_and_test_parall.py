from buildbot.plugins import schedulers
from . import properties

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
    properties.use_valgrind(),
    properties.use_callgrind(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test_parall",
    label="Build and test parallel",
    builderNames=["build_and_test_parall"],
    codebases=properties.codebaseParameter(),
    properties=BUILD_AND_TEST_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
