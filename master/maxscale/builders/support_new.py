import os
import uuid
import inspect
import re
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


def clean_build_dir():
    """Clean the build directory after the worker have completed the task"""
    return steps.ShellCommand(
        name="Clean build directory using 'git clean -fd'",
        command=["git", "clean", "-fd"],
        alwaysRun=True)


def configure_mdbci_vm_path_property():
    """Configure the MDBCI_VM_PATH property"""
    configure_mdbci_property= steps.SetProperty(
        name="Set MDBCI_VM_PATH property to $HOME/vms",
        property="MDBCI_VM_PATH",
        value=util.Interpolate("%(prop:HOME)s/vms"))

    return [get_worker_home_directory(), configure_mdbci_property]


def get_worker_home_directory():
    """Capture worker home directory into the HOME property"""
    return steps.SetPropertiesFromEnv(
        name="Get HOME variable from the worker into build property",
        variables=["HOME"])


def clean_build_intermediates():
    """Add steps to clean build intermediats created by the scripts and tools"""
    steps = []
    steps.extend(destroy_virtual_machine())
    steps.extend(remove_lock())
    return steps


def destroy_virtual_machine():
    """Destroy virtual machine if it was not destroied after the build"""
    def remote_code():
        if do_not_destroy_vm == "yes":
            print("Build VMs marked as undestroyable, doing nothing")
            sys.exit(0)

        if try_already_running == "yes":
            print("Build uses permanent VMs, doing nothing")
            sys.exit(0)

        mdbci_config="{}/{}-{}{}".format(MDBCI_VM_PATH, box, buildername, buildernumber)
        if not os.path.exists(mdbci_config):
            print("MDBCI configuration does not exist")
            sys.exit(0)

        os.system("$HOME/mdbci/mdbci destroy {}".format(mdbci_config))
    return execute_python_script(
        "Destroy leftover virtual machines", remote_code,
        ["do_not_destroy_vm", "try_already_running", "MDBCI_VM_PATH", "box", "buildername",
         "buildernumber"],
        halt_on_failure=False, flunk_on_failure=True, always_run=True)


def remove_lock():
    """Remove vagrant lock if it was left by the build script"""
    def remote_code():
        if try_already_running == "yes":
            print("Releasing lock for already running VM")
            os.remove("{}/{}_snpashot_lock".format(MDBCI_VM_PATH, box))
            sys.exit(0)

        lock_file = "{}/vagrant_lock".format(HOME)
        if not os.path.exists(lock_file):
            print("Lock file {} does not exist, doing nothing".format(lock_file))
            sys.exit(0)

        build_full_name = "{}-{}".format(buildername, buildnumber)
        locker_source = open(lock_file).read()
        if locker_source != build_full_name:
            print("Lock file was crated not by the current task, {} != {}, doing nothing".format(build_full_name, locker_source))
            sys.exit(0)

        os.remove(lock_file)

    return execute_python_script(
        "Remove leftover vagrant locks", remote_code,
        ["try_already_running", "MDBCI_VM_PATH", "box", "HOME", "buildername", "buildnumber"],
        halt_on_failure=False, flunk_on_failure=True, always_run=True)


# Following methods are internal and used to beautify the rest of the code above
def execute_script(name, script, args=[], halt_on_failure=True, flunk_on_failure=False, always_run=False, env={}):
    """Download the executable script onto the worker and execute it"""
    shell_script_path = util.Interpolate("%(prop:builddir)s/scripts/%(kw:file_name)s",
                                         file_name=str(uuid.uuid4()))

    download_step = steps.StringDownload(
        script,
        workerdest=shell_script_path,
        name="Download script to the worker: {}".format(name),
        mode=0o755,
        haltOnFailure=halt_on_failure,
        flunkOnFailure=flunk_on_failure,
        alwaysRun=always_run)

    run_step = steps.ShellCommand(
        name="Execute script: {}".format(name),
        command=[shell_script_path, *args],
        haltOnFailure=halt_on_failure,
        flunkOnFailure=flunk_on_failure,
        alwaysRun=always_run)

    remove_script = steps.ShellCommand(
        name="Remove script from worker: {}".format(name),
        command=["rm", "-f", shell_script_path],
        haltOnFailure=halt_on_failure,
        flunkOnFailure=flunk_on_failure,
        alwaysRun=True)

    return [download_step, run_step, remove_script]


def execute_python_script(name, function, properties=[], **kwargs):
    """Convert passed function to the text, prepend properties and execute in on the server"""
    code = convert_properties_to_code(properties)
    code.extend(convert_function_to_strings(function))
    code.insert(0, "#!/usr/bin/env python3")
    code_string = "\n".join(code)
    return execute_script(name, code_string,
                          args=convert_properties_to_args(properties),
                          **kwargs)


def convert_function_to_strings(function):
    lines = inspect.getsource(function)
    raw_code = lines.split("\n")[1:]
    offset = len(re.match(r"\s*", raw_code[0], re.UNICODE).group(0))
    code = []
    for line in raw_code:
        code.append(line[offset:])
    return code


def convert_properties_to_code(properties):
    code = ["import sys", "import os", "import os.path", "import shutil"]
    for property in enumerate(properties, start=1):
        code.append("{} = sys.argv[{}]".format(property[1], property[0]))
    return code


def convert_properties_to_args(properties):
    args = []
    for property in properties:
        args.append(util.Property(property))
    return args
