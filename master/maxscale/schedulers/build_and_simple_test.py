from buildbot.plugins import util, schedulers
from maxscale.change_source.maxscale import check_branch_fn
from maxscale.config import constants
from . import properties


CHANGE_SOURCE_SCHEDULER = schedulers.SingleBranchScheduler(
    name="build_and_simple_test_on_push",
    change_filter=util.ChangeFilter(project='maxscale', branch_fn=check_branch_fn),
    treeStableTimer=60,
    builderNames=["build_and_simple_test"],
    codebases=constants.MAXSCALE_CODEBASE
)


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_simple_test_force",
    buttonName="Build and simple test",
    builderNames=["build_and_simple_test"],
    codebases=properties.codebaseParameter(),
    properties=[
        properties.build_target(),
        properties.build_experimental_features(),
        properties.backend_database(),
        properties.database_version(),
        properties.keep_virtual_machines(),
        properties.try_already_running(),
        properties.test_set(),
        properties.ci_url(),
        properties.backend_use_ssl(),
        properties.maxscale_threads(),
        properties.sysbench_threads(),
    ]
)

SCHEDULERS = [CHANGE_SOURCE_SCHEDULER, MANUAL_SCHEDULER]
