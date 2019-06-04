import os
from buildbot.plugins import util
from maxscale.config import constants
from maxscale.config import workers

propertyNamesAndFunc = {}


def build_box(default=constants.BOXES[0]):
    return util.ChoiceStringParameter(
        name="box",
        label="Box",
        choices=constants.BOXES,
        default=default)
propertyNamesAndFunc.update({"box": build_box})


def build_full_name():
    return util.StringParameter(
        name="build_full_name",
        label="Build full name ('JOB_NAME-BUILD_ID')",
        size=50)
propertyNamesAndFunc.update({"build_full_name": build_full_name})


def build_name():
    return util.StringParameter(
        name="name",
        label="Name of this build",
        size=50,
        default="test01")
propertyNamesAndFunc.update({"name": build_name})


def build_target(default="develop"):
    return util.StringParameter(
        name="target",
        label="Target",
        size=50,
        default=default)
propertyNamesAndFunc.update({"target": build_target})


def cmake_flags(default=constants.DEFAULT_CMAKE_FLAGS):
    return util.StringParameter(
        name="cmake_flags",
        label="CMake flags",
        size=50,
        default=default)
propertyNamesAndFunc.update({"cmake_flags": cmake_flags})


def keep_virtual_machines():
    return util.ChoiceStringParameter(
        name="do_not_destroy_vm",
        label="Keep virtual machines running",
        choices=['no', 'yes'],
        default='no')
propertyNamesAndFunc.update({"do_not_destroy_vm": keep_virtual_machines})


def build_experimental_features():
    return util.ChoiceStringParameter(
        name="build_experimental",
        label="Build experimental features",
        choices=["yes", "no"],
        default="yes")
propertyNamesAndFunc.update({"build_experimental": build_experimental_features})


def repository_path():
    return util.StringParameter(
        name="repo_path",
        label="Repository path",
        size=50,
        default="repository")
propertyNamesAndFunc.update({"repo_path": repository_path})


def try_already_running():
    return util.ChoiceStringParameter(
        name="try_already_running",
        label="Try already running",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"try_already_running": try_already_running})


def run_upgrade_test():
    return util.ChoiceStringParameter(
        name="run_upgrade_test",
        label="Run upgrade test",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"run_upgrade_test": run_upgrade_test})


def old_target():
    return util.StringParameter(
        name="old_target",
        label="Old target",
        size=50,
        default="2.1.9")
propertyNamesAndFunc.update({"old_target": old_target})


def ci_url():
    return util.StringParameter(
        name="ci_url",
        label="ci url",
        size=50,
        default=constants.CI_SERVER_URL)
propertyNamesAndFunc.update({"ci_url": ci_url})


def backend_database():
    return util.ChoiceStringParameter(
        name="product",
        label="Product",
        choices=['mariadb', 'mysql'],
        default='mariadb')
propertyNamesAndFunc.update({"product": backend_database})


def database_version():
    return util.ChoiceStringParameter(
        name="version",
        label="Version",
        choices=constants.DB_VERSIONS,
        default=constants.DB_VERSIONS[0])
propertyNamesAndFunc.update({"version": database_version})


def test_set():
    return util.StringParameter(
        name="test_set",
        label="Test set",
        size=50,
        default="-LE HEAVY")
propertyNamesAndFunc.update({"test_set": test_set})


def backend_use_ssl():
    return util.ChoiceStringParameter(
        name="backend_ssl",
        label="Backend ssl",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"backend_ssl": backend_use_ssl})


def smoke_tests():
    return util.ChoiceStringParameter(
        name="smoke",
        label="Run fast versions of every test",
        choices=["yes", "no"],
        default="yes")
propertyNamesAndFunc.update({"smoke": smoke_tests})


def big_number_of_vms():
    return util.ChoiceStringParameter(
        name="big",
        label="Use larger number of VMs",
        choices=["yes", "no"],
        default="yes")
propertyNamesAndFunc.update({"big": big_number_of_vms})


def snapshot_name():
    return util.StringParameter(
        name="snapshot_name",
        label="Snapshot name",
        size=50,
        default="clean")
propertyNamesAndFunc.update({"snapshot_name": snapshot_name})


def use_snapshots():
    return util.ChoiceStringParameter(
        name="use_snapshots",
        label="Use snapshots",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"use_snapshots": use_snapshots})


def test_logs_directory():
    return util.StringParameter(
        name="logs_dir",
        label="Logs dir",
        size=50,
        default="LOGS")
propertyNamesAndFunc.update({"logs_dir": test_logs_directory})


def do_not_revert_virtual_machines():
    return util.ChoiceStringParameter(
        name="no_vm_revert",
        label="No vm revert",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"no_vm_revert": do_not_revert_virtual_machines})


def test_branch():
    return util.StringParameter(
        name="test_branch",
        label="Test branch",
        size=100,
        default="master")
propertyNamesAndFunc.update({"test_branch": test_branch})


def test_template():
    return util.ChoiceStringParameter(
        name="template",
        label="Template",
        choices=['default', 'clustrix'],
        default='default')
propertyNamesAndFunc.update({"template": test_template})


def configuration_to_clone():
    return util.StringParameter(
        name="config_to_clone",
        label="Config to clone",
        size=50)
propertyNamesAndFunc.update({"config_to_clone": configuration_to_clone})


def extractDefaultValues(properties):
    """Create a dictionary of properties default values"""
    defaults = {}
    for propertyDefinition in properties:
        defaults[propertyDefinition.name] = propertyDefinition.default
    return defaults


def buildBoxCheckboxContainer():
    """
    Creates a parameter which contains checkboxes
    for each OS presented in the BUILD_ALL_BOXES array
    """
    return util.NestedParameter(
        name="build_box_checkbox_container",
        label="Build boxes",
        maxsize=300,
        columns=1,
        fields=[buildBoxCheckbox(box) for box in constants.BUILD_ALL_BOXES],
        default=dict((box, True) for box in constants.BUILD_ALL_BOXES))
propertyNamesAndFunc.update({"build_box_checkbox_container": buildBoxCheckboxContainer})


def buildBoxCheckbox(box):
    """Creates a checkbox parameter for a given box"""
    return util.BooleanParameter(
        name=box,
        label=box,
        default=True)


def codebaseParameter():
    return [util.CodebaseParameter(
        "",
        label="Main repository",
        branch=util.StringParameter(name="branch",
                                    default=constants.MAXSCALE_CODEBASE[""]["branch"]),
        revision=util.FixedParameter(name="revision",
                                     default=constants.MAXSCALE_CODEBASE[""]["revision"]),
        project=util.FixedParameter(name="project", default=""),
        repository=util.StringParameter(name="repository",
                                        default=constants.MAXSCALE_CODEBASE[""]["repository"]),
    )]


def codebaseMdbciParameter():
    return [util.CodebaseParameter(
        "",
        label="Main repository",
        branch=util.StringParameter(name="branch",
                                    default=constants.MDBCI_CODEBASE[""]["branch"]),
        revision=util.FixedParameter(name="revision",
                                     default=constants.MDBCI_CODEBASE[""]["revision"]),
        project=util.FixedParameter(name="project", default=""),
        repository=util.StringParameter(name="repository",
                                        default=constants.MDBCI_CODEBASE[""]["repository"]),
    )]


def versionNumber():
    return util.StringParameter(
        name="version_number",
        label="The version number of this release in x.y.z format"
    )
propertyNamesAndFunc.update({"version_number": versionNumber})


def host(default="max-tst-01"):
    """Host of the used group of workers"""
    return util.ChoiceStringParameter(
        name="host",
        label="Host",
        choices=list(set(map(lambda worker: worker["host"], workers.WORKER_CREDENTIALS))),
        default=default
    )
propertyNamesAndFunc.update({"host": host})


def maxscale_threads():
    return util.StringParameter(
        name="maxscale_threads",
        label="The value of 'threads' parameter in the maxscale.cnf",
        default="8"
    )
propertyNamesAndFunc.update({"maxscale_threads": maxscale_threads})


def sysbench_threads():
    return util.StringParameter(
        name="sysbench_threads",
        label="Number of sysbench threads",
        default="16"
    )
propertyNamesAndFunc.update({"sysbench_threads": sysbench_threads})


def perf_cnf_template(default="base.cnf.erb"):
    """Template for Maxscale.cnf for performance tests"""
    return util.ChoiceStringParameter(
        name="perf_cnf_template",
        label="Mascale.cnf template",
        choices=constants.PERF_CNF_TEMPLATES,
        default=default
    )
propertyNamesAndFunc.update({"perf_cnf_template": perf_cnf_template})


def perf_port(default="4006"):
    """Maxscale port for performance tests"""
    return util.ChoiceStringParameter(
        name="perf_port",
        label="Maxscale port to which sysbench connects",
        choices=constants.PERF_PORTS,
        default=default
    )
propertyNamesAndFunc.update({"perf_port": perf_port})


def perf_runtime():
    return util.IntParameter(
        name="perf_runtime",
        label="Time to run sysbench",
        default=121
    )
propertyNamesAndFunc.update({"perf_runtime": perf_runtime})


def use_valgrind():
    return util.ChoiceStringParameter(
        name="use_valgrind",
        label="Use valgrind",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"use_valgrind": use_valgrind})


def use_callgrind():
    return util.ChoiceStringParameter(
        name="use_callgrind",
        label="Use callgrind",
        choices=["no", "yes"],
        default="no")
propertyNamesAndFunc.update({"use_callgrind": use_callgrind})


def version_number():
    return util.StringParameter(
        name="version_number",
        label="version_number",
        default="2.x.x")


def getPropertyByName(name):
    if name not in propertyNamesAndFunc:
        return None
    return propertyNamesAndFunc[name]()
