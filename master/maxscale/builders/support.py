import os
from buildbot.plugins import steps, util
from . import builders_config


def clone_repository():
    """Clone MaxScale repository using default configuration options"""
    return steps.Git(
        name=util.Interpolate("Clone data from repository '%(prop:repository)s', branch '%(prop:branch)s'"),
        repourl=util.Property('repository'),
        branch=util.Property('branch'),
        mode='incremental',
        haltOnFailure=True)


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
        command=["sh", shell_script_path],
        haltOnFailure=halt_on_failure,
        alwaysRun=always_run,
        env={})

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
    steps.extend(remove_lock())
    return steps


def destroy_virtual_machine():
    """Run the VM destroy script"""
    return execute_shell_script("run_destroy.sh",
                                halt_on_failure=True,
                                always_run=True,
                                env=env_properties("name", "do_not_destroy_vm",
                                                   "try_already_running"))


def smart_remove_lock():
    """Try to smartly remove lock"""
    return execute_shell_script("run_smart_remove_lock.sh",
                                halt_on_failure=True,
                                always_run=True,
                                env=env_properties("build_full_name"))


def remove_lock():
    """Remove lock manually"""
    return execute_shell_script("run_remove_lock.sh",
                                halt_on_failure=True,
                                always_run=True,
                                env=env_properties("try_already_running"))


def env_properties(*keys):
    """Create an environment array from properties"""
    env = {}
    for key in keys:
        env[key] = util.Property(key)
    return env
