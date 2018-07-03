import os
from buildbot.plugins import util
from maxscale.config import constants


def build_box():
    return util.ChoiceStringParameter(
        name="box",
        label="Box",
        choices=constants.BOXES,
        default=constants.BOXES[0])


def build_full_name():
    return util.StringParameter(
        name="build_full_name",
        label="Build full name ('JOB_NAME-BUILD_ID')",
        size=50)


def build_name():
    return util.StringParameter(
        name="name",
        label="Name of this build",
        size=50,
        default="test01")


def build_target():
    return util.StringParameter(
        name="target",
        label="Target",
        size=50,
        default="develop")


def cmake_flags():
    return util.StringParameter(
        name="cmake_flags",
        label="CMake flags",
        size=50,
        default=constants.DEFAULT_CMAKE_FLAGS)


def keep_virtual_machines():
    return util.ChoiceStringParameter(
        name="do_not_destroy_vm",
        label="Keep virtual machines running",
        choices=['no', 'yes'],
        default='no')


def build_experimental_features():
    return util.ChoiceStringParameter(
        name="build_experimental",
        label="Build experimental features",
        choices=["yes", "no"],
        default="yes")


def repository_path():
    return util.StringParameter(
        name="repo_path",
        label="Repository path",
        size=50,
        default=os.environ['HOME'] + "/repository")


def try_already_running():
    return util.ChoiceStringParameter(
        name="try_already_running",
        label="Try already running",
        choices=["no", "yes"],
        default="no")


def run_upgrade_test():
    return util.ChoiceStringParameter(
        name="run_upgrade_test",
        label="Run upgrade test",
        choices=["no", "yes"],
        default="no")


def old_target():
    return util.StringParameter(
        name="old_target",
        label="Old target",
        size=50,
        default="2.1.9")


def ci_url():
    return util.StringParameter(
        name="ci_url",
        label="ci url",
        size=50,
        default=constants.CI_SERVER_URL)


def backend_database():
    return util.ChoiceStringParameter(
        name="product",
        label="Product",
        choices=['mariadb', 'mysql'],
        default='mariadb')


def database_version():
    return util.ChoiceStringParameter(
        name="version",
        label="Version",
        choices=constants.DB_VERSIONS,
        default=constants.DB_VERSIONS[0])


def test_set():
    return util.StringParameter(
        name="test_set",
        label="Test set",
        size=50,
        default="-LE HEAVY")


def backend_use_ssl():
    return util.ChoiceStringParameter(
        name="backend_ssl",
        label="Backend ssl",
        choices=["no", "yes"],
        default="no")


def maxscale_threads():
    return util.StringParameter(
        name="maxscale_threads",
        label="Maxscale threads",
        size=4,
        default="8")


def sysbench_threads():
    return util.StringParameter(
        name="sysbench_threads",
        label="Sysbench threads",
        size=4,
        default="128")


def smoke_tests():
    return util.ChoiceStringParameter(
        name="smoke",
        label="Run fast versions of every test",
        choices=["yes", "no"],
        default="yes")


def big_number_of_vms():
    return util.ChoiceStringParameter(
        name="big",
        label="Use larger number of VMs",
        choices=["yes", "no"],
        default="yes")


def snapshot_name():
    return util.StringParameter(
        name="snapshot_name",
        label="Snapshot name",
        size=50,
        default="clean")


def use_snapshots():
    return util.ChoiceStringParameter(
        name="use_snapshots",
        label="Use snapshots",
        choices=["no", "yes"],
        default="no")


def test_logs_directory():
    return util.StringParameter(
        name="logs_dir",
        label="Logs dir",
        size=50,
        default=os.environ['HOME'] + "/LOGS")


def do_not_revert_virtual_machines():
    return util.ChoiceStringParameter(
        name="no_vm_revert",
        label="No vm revert",
        choices=["no", "yes"],
        default="no")


def test_branch():
    return util.StringParameter(
        name="test_branch",
        label="Test branch",
        size=100,
        default="master")


def test_template():
    return util.ChoiceStringParameter(
        name="template",
        label="Template",
        choices=['default', 'nogalera', 'twomaxscales'],
        default='default')


def configuration_to_clone():
    return util.StringParameter(
        name="config_to_clone",
        label="Config to clone",
        size=50)


def extractDefaultValues(properties):
    """Create a dictionary of properties default values"""
    defaults = {}
    for propertyDefinition in properties:
        defaults[propertyDefinition.name] = propertyDefinition.default
    return defaults
