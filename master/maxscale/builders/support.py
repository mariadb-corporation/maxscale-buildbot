import os
import uuid
from buildbot.plugins import steps, util
from . import builders_config


def clone_repository():
    """Clone MaxScale repository using default configuration options"""
    return steps.Git(
        name=util.Interpolate("Clone repository '%(prop:repository)s', branch '%(prop:branch)s'"),
        repourl=util.Property('repository'),
        branch=util.Property('branch'),
        mode='incremental',
        haltOnFailure=True)


def get_worker_home_directory():
    """Capture worker home directory into the HOME property"""
    return steps.SetPropertiesFromEnv(variables=["HOME"])


def execute_shell_script(file_name, halt_on_failure=True, always_run=False, env={}):
    """Download shell script to the worker and execute it"""
    shell_script_path = util.Interpolate("%(prop:builddir)s/%(kw:path)s/%(kw:file_name)s",
                                         path=builders_config.WORKER_SHELL_SCRIPTS_RELATIVE_PATH,
                                         file_name=file_name)

    download_step = steps.FileDownload(
        name="Download shell script '{}' to the worker".format(file_name),
        mastersrc=os.path.join(os.getcwd(), "shell_scripts", file_name),
        workerdest=shell_script_path,
        mode=0o755,
        haltOnFailure=halt_on_failure,
        alwaysRun=always_run)

    run_step = steps.ShellCommand(
        name="Run the '{}' script".format(file_name),
        command=['sh', shell_script_path],
        haltOnFailure=halt_on_failure,
        alwaysRun=always_run,
        env=env)

    return [download_step, run_step]


def execute_script(name, script, halt_on_failure=True, fluke_on_falilure=False, always_run=False, env={}):
    """Download the executable script onto the worker and execute it"""
    shell_script_path = util.Interpolate("%(prop:builddir)s/../scripts/%(kw:file_name)s",
                                         file_name=str(uuid.uuid4()))

    download_step = steps.StringDownload(
        script,
        workerdest=shell_script_path,
        name="Download executable script '{}' to the worker".format(name),
        mode=0o755,
        hailtOnFailure=halt_on_failure,
        flukeOnFailure=fluke_on_falilure,
        alwaysRun=always_run)

    run_step = steps.ShellCommand(
        name="Run the '{}' script".format(name),
        command=[shell_script_path],
        hailtOnFailure=halt_on_failure,
        flukeOnFailure=fluke_on_falilure,
        alwaysRun=always_run)

    return [download_step, run_step]


def clean_build_dir():
    """Clean the build directory after the worker have completed the task"""
    return steps.ShellCommand(
        name="Workspace cleanup",
        command=["git", "clean", "-fd"],
        alwaysRun=True)


def clean_build_intermediates():
    """Add steps to clean build intermediats created by the scripts and tools"""
    steps = []
    steps.extend(destroy_virtual_machine())
    steps.extend(smart_remove_lock())
    return steps


def destroy_virtual_machine():
    """Run the VM destroy script"""
    return execute_shell_script("run_destroy.sh",
                                halt_on_failure=False,
                                always_run=True,
                                env=env_properties("name", "MDBCI_VM_PATH"))


def smart_remove_lock():
    """Try to smartly remove lock"""
    return execute_shell_script("run_smart_remove_lock.sh",
                                halt_on_failure=False,
                                always_run=True,
                                env=env_properties("build_full_name", "MDBCI_VM_PATH"))


def remove_lock():
    """Remove lock manually"""
    return execute_shell_script("run_remove_lock.sh",
                                halt_on_failure=False,
                                always_run=True,
                                env=env_properties("MDBCI_VM_PATH"))


def env_properties(*keys):
    """Create an environment array from properties"""
    env = {}
    for key in keys:
        env[key] = util.Property(key)
    return env


def destroy_virtual_machine_script():
    """Destroy virtual machine if it was not destroied after the build"""
    code = util.Interpolate("""
    #!/bin/bash
    set -xe

    if [ "%(prop:do_not_destroy_vm)s" = "yes" ]; then
        echo "Config marked as undestroyable, exiting"
        exit 0
    fi

    if [ "%(prop:try_already_running)" = "yes" ]; then
        echo "Config uses permanent VM, exiting"
        exit 0
    fi

    mdbci_config=$MDBCI_VM_PATH/$name
    if [ ! -e "$mdbci_config" ]; then
        exit 0
    fi

    $HOME/mdbci/mdbci destroy $mdbci_config
    """,)
