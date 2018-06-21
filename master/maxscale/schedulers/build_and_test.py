from buildbot.plugins import schedulers
from . import properties
from . import common


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test",
    label="Build and test",
    builderNames=["build_and_test"],
    codebases=[
        common.maxscale_codebase()
    ],
    properties=[
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
        properties.backend_use_ssl()
    ]
)

SCHEDULERS = [MANUAL_SCHEDULER]
