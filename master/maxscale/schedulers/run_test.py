from buildbot.plugins import schedulers
from . import common
from . import properties


REPOSITORY_SCHEDULER = schedulers.Triggerable(
    name="run_test",
    builderNames=["run_test"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_test_force",
    buttonName="Run tests",
    builderNames=["run_test"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_name(),
        properties.build_target(),
        properties.build_box(),
        properties.backend_database(),
        properties.database_version(),
        properties.keep_virtual_machines(),
        properties.test_set(),
        properties.ci_url(),
        properties.smoke_tests(),
        properties.big_number_of_vms(),
        properties.backend_use_ssl(),
        properties.use_snapshots(),
        properties.test_logs_directory(),
        properties.do_not_revert_virtual_machines(),
        properties.test_template(),
        properties.configuration_to_clone(),
    ]
)

SCHEDULERS = [REPOSITORY_SCHEDULER, MANUAL_SCHEDULER]
