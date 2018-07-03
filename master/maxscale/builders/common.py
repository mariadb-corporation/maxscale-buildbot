from buildbot.plugins import util, steps
from buildbot.process.buildstep import ShellMixin
from twisted.internet import defer
from . import support

def cloneRepository():
    """Clone MaxScale repository using default configuration options"""
    return [steps.Git(
        name=util.Interpolate("Clone repository '%(prop:repository)s', branch '%(prop:branch)s'"),
        repourl=util.Property('repository'),
        branch=util.Property('branch'),
        mode='incremental',
        haltOnFailure=True)]


def cleanBuildDir():
    """Clean the build directory after the worker have completed the task"""
    return [steps.ShellCommand(
        name="Clean build directory using 'git clean -fd'",
        command=["git", "clean", "-fd"],
        alwaysRun=True)]


def configureMdbciVmPathProperty():
    """Configure the MDBCI_VM_PATH property"""
    buildSteps = getWorkerHomeDirectory()
    configureMdbciProperty = steps.SetProperty(
        name="Set MDBCI_VM_PATH property to $HOME/vms",
        property="MDBCI_VM_PATH",
        value=util.Interpolate("%(prop:HOME)s/vms"))

    buildSteps.append(configureMdbciProperty)
    return buildSteps


def getWorkerHomeDirectory():
    """Capture worker home directory into the HOME property"""
    return [steps.SetPropertiesFromEnv(
        name="Get HOME variable from the worker into build property",
        variables=["HOME"])]


def cleanBuildIntermediates():
    """Add steps to clean build intermediats created by the scripts and tools"""
    cleanSteps = []
    cleanSteps.extend(destroyVirtualMachine())
    cleanSteps.extend(removeLock())
    return cleanSteps


def destroyVirtualMachine():
    """Destroy virtual machine if it was not destroied after the build"""
    def remoteCode():
        if do_not_destroy_vm == "yes":
            print("Build VMs marked as undestroyable, doing nothing")
            sys.exit(0)

        if try_already_running == "yes":
            print("Build uses permanent VMs, doing nothing")
            sys.exit(0)

        mdbciConfig = "{}/{}-{}{}".format(MDBCI_VM_PATH, box, buildername, buildnumber)
        if not os.path.exists(mdbciConfig):
            print("MDBCI configuration does not exist")
            sys.exit(0)

        os.system("$HOME/mdbci/mdbci destroy {}".format(mdbciConfig))

    return support.executePythonScript(
        "Destroy leftover virtual machines", remoteCode,
        haltOnFailure=False, alwaysRun=True)


def removeLock():
    """Remove vagrant lock if it was left by the build script"""
    def remoteCode():
        if try_already_running == "yes":
            print("Releasing lock for already running VM")
            os.remove("{}/{}_snpashot_lock".format(MDBCI_VM_PATH, box))
            sys.exit(0)

        lockFile = "{}/vagrant_lock".format(HOME)
        if not os.path.exists(lockFile):
            print("Lock file {} does not exist, doing nothing".format(lockFile))
            sys.exit(0)

        buildFullName = "{}-{}".format(buildername, buildnumber)
        lockerSource = open(lockFile).read()
        if lockerSource != buildFullName:
            print("Lock file was crated not by the current task, {} != {}, doing nothing".
                  format(buildFullName, lockerSource))
            sys.exit(0)

        os.remove(lockFile)

    return support.executePythonScript(
        "Remove leftover vagrant locks", remoteCode,
        haltOnFailure=False, alwaysRun=True)


def save_env_to_property(rc, stdout, stderr):
    ''' Function used as the extrat_fn function for SetProperty class
        This takes the output from env command and creates a dictionary of
        the environment, the result of which is stored in a property names
        env'''
    if not rc:
        env_list = [l.strip() for l in stdout.split('\n')]
        env_dict = {l.split('=', 1)[0]: l.split('=', 1)[1] for l in
                    env_list if len(l.split('=', 1)) == 2}
        return {'env': env_dict}


@util.renderer
def clean_workspace_command(props):
    return ['git', 'clean', '-fd']


class SetDefaultPropertiesStep(ShellMixin, steps.BuildStep):
    name = 'Set default properties'

    def __init__(self, default_properties, **kwargs):
        self.default_properties = default_properties
        kwargs = self.setupShellMixin(kwargs, prohibitArgs=['command'])
        steps.BuildStep.__init__(self, **kwargs)

    @defer.inlineCallbacks
    def run(self):
        for property_name, value in self.default_properties.items():
            if self.getProperty(property_name) is None:
                self.setProperty(
                    property_name,
                    value,
                    'setDefaultProperties'
                )
                cmd = yield self.makeRemoteShellCommand(
                    command=['echo', "Set default property: {}={}".format(property_name, value)])
                yield self.runCommand(cmd)
        defer.returnValue(0)
