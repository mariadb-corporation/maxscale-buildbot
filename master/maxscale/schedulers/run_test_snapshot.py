from buildbot.plugins import schedulers
from . import common
from . import properties


REPOSITORY_SCHEDULER = schedulers.Triggerable(
    name="run_test_snapshot",
    builderNames=["run_test_snapshot"],
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_test_snapshot_force",
    buttonName="Run test snapshots",
    builderNames=["run_test_snapshot"],
    codebases=[
        common.maxscale_codebase(),
    ],
    properties=[
        properties.build_name(),
        properties.snapshot_name(),
        properties.build_target(),
        properties.build_box(),
        properties.backend_database(),
        properties.database_version(),
        properties.test_set(),
        properties.ci_url(),
        properties.smoke_tests(),
        properties.big_number_of_vms(),
        properties.backend_use_ssl(),
        properties.test_logs_directory(),
        properties.test_template(),
        properties.test_branch()
    ]
)

SCHEDULERS = [REPOSITORY_SCHEDULER, MANUAL_SCHEDULER]
