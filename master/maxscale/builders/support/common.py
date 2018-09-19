import datetime
from buildbot.plugins import util, steps
from buildbot.process.buildstep import ShellMixin
from buildbot.process.results import SKIPPED
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shellsequence import ShellSequence
from twisted.internet import defer
from maxscale.builders.support import support
from maxscale import builders
from maxscale import workers


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
        command=["rm", "-rf", util.Property('builddir')],
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
        if not os.path.exists(mdbciConfig):
            print("MDBCI configuration does not exist")
            sys.exit(0)

        os.system("$HOME/mdbci/mdbci destroy {}".format(mdbciConfig))

    def shouldRun(step):
        if step.getProperty("try_already_running") == "yes" or step.getProperty("do_not_destroy_vm") == "yes":
            return False
        return True

    return support.executePythonScript(
        "Destroy leftover virtual machines", remoteCode,
        haltOnFailure=False, alwaysRun=True, doStepIf=shouldRun)


def removeSnapshotLock():
    """
    Compares $build_full_name and $HOME/mdbci/${name}_snapshot_lock content
    and calls remove lock if they are equal
    """
    def remoteCode():
        lockFile = "{}/{}_snapshot_lock".format(MDBCI_VM_PATH, name)
        if not os.path.exists(lockFile):
            print("Lock file {} does not exist, doing nothing".format(lockFile))
            sys.exit(0)

        buildFullName = "{}-{}".format(buildername, buildnumber)
        lockerSource = open(lockFile).read().strip()
        if lockerSource != buildFullName:
            print("Lock file was created not by the current task, {} != {}, doing nothing".
                  format(buildFullName, lockerSource))
            sys.exit(0)
        os.remove(lockFile)
        sys.exit(0)

    return support.executePythonScript(
        "Remove leftover snapshot locks", remoteCode,
        haltOnFailure=False, alwaysRun=True)


def removeLock():
    """Remove vagrant lock if it was left by the build script"""
    def remoteCode():
        lockFile = "{}/vagrant_lock".format(HOME)
        if os.path.exists(lockFile):
            buildFullName = "{}-{}".format(buildername, buildnumber)
            lockerSource = open(lockFile).read().strip()
            if lockerSource == buildFullName:
                os.remove(lockFile)
            else:
                print("Lock file was created not by the current task, {} != {}, doing nothing".
                      format(buildFullName, lockerSource))
        else:
            print("Lock file {} does not exist, doing nothing".format(lockFile))

        if try_already_running == "yes":
            snapshotLockFile = "{}/{}_snapshot_lock".format(MDBCI_VM_PATH, box)
            if os.path.exists(snapshotLockFile):
                print("Releasing lock for already running VM")
                os.remove(snapshotLockFile)
        sys.exit(0)

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


class StdoutShellCommand(ShellCommand):
    """
    Runs single shell command on a remote worker
    and outputs stdout into a separate logfile
    """
    def commandComplete(self, cmd):
        self.addCompleteLog('stdout', cmd.stdout)


def getFormattedDateTime(format):
    @util.renderer
    def formatDateTime(properties):
        return datetime.datetime.now().strftime(format)

    return formatDateTime


def setMissingTarget():
    return [steps.SetProperty(
        name=util.Interpolate("Set 'target' property"),
        property="target",
        value=util.Interpolate("%(prop:branch)s-buildbot-%(kw:startTime)s",
                               startTime=getFormattedDateTime("%b%d-%H:%M:%S")),
        doStepIf=lambda step: step.build.getProperty('target') is None,
        hideStepIf=lambda results, s: results == SKIPPED
    )]


def assignWorker(builder, workerForBuilerList, buildRequest):
    """
    Returns available worker for a builder
    filtered by the scheduler which triggered build and by the giver task-host mapping
    See 'nextWorker' at http://docs.buildbot.net/current/manual/cfg-builders.html#builder-configuration
    """
    workerNames = workers.workerNames(buildRequest.properties.getProperty("host", default=""))
    availableWorkers = filter(lambda wfb: wfb.worker.workername in workerNames, workerForBuilerList)
    for workerForBuilder in availableWorkers:
        if workerForBuilder.isAvailable():
            buildRequest.properties.setProperty("host", workers.workerToHostMap()[workerForBuilder.worker.workername],
                                                "Assign worker")
            return workerForBuilder


def assignBestHost(builder, workersForBuilders, buildRequest):
    """
    Returns availble workersForBuilders on a host with the least tasks running
    :param builder: Builder for this task
    :param workersForBuilders: List of workerForBuilders
    :param buildRequest: build request
    :return: List of workersForBuilders for a specific host
    """
    # Go directly to worker assignment if host in specified
    if buildRequest.properties.getProperty("host"):
        return assignWorker(buildRequest, workersForBuilders, buildRequest)

    workerToHostMap = workers.workerToHostMap()
    occupiedWorkers = {}
    hostToWorkersMap = {}
    availableWFB = []

    for name, host in workerToHostMap.items():
        hostToWorkersMap[host] = hostToWorkersMap.get(host, []) + [name]
        occupiedWorkers[host] = len(hostToWorkersMap[host])

    for wfb in workersForBuilders:
        if wfb.isAvailable() and builder.name == wfb.builder_name:
            occupiedWorkers[workerToHostMap[wfb.worker.workername]] -= 1

    bestHost = sorted(occupiedWorkers.items(), key=lambda item: item[1])[0]
    for wfb in workersForBuilders:
        if wfb.worker.workername in hostToWorkersMap[bestHost[0]]:
            availableWFB.append(wfb)

    return assignWorker(builder, availableWFB, buildRequest)


def generateRepositories():
    return [steps.ShellCommand(
        name="Generate product repositories",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/mdbci"), "generate-product-repositories"],
        haltOnFailure=True
    )]


def syncRepod():
    return [RsyncShellSequence(name="Synchronizing ~/.config/mdbci/repo.d among workers",
                               haltOnFailure=False)]


class RsyncShellSequence(ShellSequence):
    """
    rsync ~/.config/mdbci/repo.d directory from current worker
    to every other unique worker's host
    """
    def createRsyncSequence(self, hosts):
        return [util.ShellArg(command="rsync -r ~/.config/mdbci/repo.d "
                                      "vagrant@{}.mariadb.com:~/.config/mdbci/repo.d".format(host),
                              logfile="rsync to {}.mariadb.com".format(host)) for host in hosts]

    def getRemoteWorkersHosts(self):
        hosts = set()
        currentHost = None
        for worker in workers.WORKER_CREDENTIALS:
            if worker["name"] != self.getProperty("workername"):
                hosts.add(worker["host"])
            else:
                currentHost = worker["host"]
        hosts.discard(currentHost)
        return hosts

    def run(self):
        hosts = self.getRemoteWorkersHosts()
        self.commands = self.createRsyncSequence(hosts)
        if not hosts:
            self.descriptionDone = "No remote hosts found"
        return self.runShellSequence(self.commands)
