from buildbot.plugins import schedulers, util
from . import properties
from maxscale.change_source.maxscale import get_test_set_by_branch
from maxscale.config import constants
from maxscale.config.branches_list_file import VALGRIND_BRANCHES_LIST
from maxscale.config.branches_list_file import NIGHTLY_BRANCHES_LIST
from maxscale.config.branches_list_file import DIFF_DISTRO_BRANCHES_LIST
from maxscale.builders.support.common import TargetInitOptions


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


