import datetime
from collections import defaultdict
from buildbot.plugins import util, steps
from buildbot.process.buildstep import ShellMixin
from buildbot.process.results import SKIPPED
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shellsequence import ShellSequence
from buildbot.steps.trigger import Trigger
from twisted.internet import defer
from maxscale.builders.support import support
from maxscale.change_source.maxscale import get_test_set_by_branch
from maxscale import workers
from enum import IntEnum
from maxscale.config import constants


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
        value=util.Interpolate("%(prop:HOME)s/vms"),
        hideStepIf=True,
    )

    buildSteps.append(configureMdbciProperty)
    return buildSteps


def runMdbciCommand(name, *command):
    """Run the MDBCI with the specified command"""
    return steps.ShellCommand(
        name=name,
        command=[util.Interpolate("%(prop:HOME)s/mdbci/mdbci"), *command],
        timeout=1800
    )


def generateMdbciRepositoryForTarget():
    """Generate repository configuration for the target specified by the property target"""
    return runMdbciCommand(
        util.Interpolate("Generate new repo descriptions for %(prop:target)s"),
        "generate-product-repositories", "--product", "maxscale_ci", "--product-version", util.Property("target")
    )


def getWorkerHomeDirectory():
    """Capture worker home directory into the HOME property"""
    return [steps.SetPropertiesFromEnv(
        name="Get HOME variable from the worker into build property",
        hideStepIf=True,
        variables=["HOME"])]


def cleanBuildIntermediates():
    """Add steps to clean build intermediats created by the scripts and tools"""
    cleanSteps = []
    cleanSteps.extend(destroyVirtualMachine())
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
    """
    Creates renderer which return formatted datetime
    :param format: format of datetime string
    :return: rendered for datetime
    """
    @util.renderer
    def formatDateTime(properties):
        return datetime.datetime.now().strftime(format)

    return formatDateTime


class TargetInitOptions(IntEnum):
    GENERATE = 1
    SET_FROM_BRANCH = 2


def initTargetProperty():
    """
    Sets 'target' property of the build to:
        - <branch>-buildbot-<starttime> if it isn't set yet or property 'targetInitMode' is TargetInitOptions.GENERATE;
        - <branch> if property 'targetInitMode' is TargetInitOptions.SET_FROM_BRANCH.
    :return: list of steps
    """
    return [
        steps.SetProperty(
            name=util.Interpolate("Set 'target' property"),
            property="target",
            value=util.Interpolate("%(prop:branch)s-buildbot-%(kw:startTime)s",
                                   startTime=getFormattedDateTime("%Y-%b-%d-%H-%M-%S")),
            doStepIf=lambda step: step.build.getProperty('target') is None and
                     step.build.getProperty('targetInitMode') is None or
                     step.build.getProperty('targetInitMode') == TargetInitOptions.GENERATE,
            hideStepIf=lambda results, s: results == SKIPPED
        ),
        steps.SetProperty(
            name=util.Interpolate("Set 'target' property"),
            property="target",
            value=util.Property("branch"),
            doStepIf=lambda step: step.build.getProperty('targetInitMode') == TargetInitOptions.SET_FROM_BRANCH,
            hideStepIf=lambda results, s: results == SKIPPED
        )
    ]


class NameInitOptions(IntEnum):
    GENERATE = 1
    KEEP_ORIGINAL = 2


def initNameProperty():
    """
    Sets 'name' property of the build to:
        - <branch>-buildbot-<starttime> if it isn't set yet or property 'nameInitMode' is NameInitOptions.GENERATE;
        - <name> if property 'nameInitMode' is NameInitOptions.KEEP_ORIGINAL.
    :return: list of steps
    """
    return [
        steps.SetProperty(
            name=util.Interpolate("Set 'name' property"),
            property="name",
            value=util.Interpolate("%(prop:branch)s-buildbot-%(kw:startTime)s",
                                   startTime=getFormattedDateTime("%Y-%b-%d-%H-%M-%S")),
            doStepIf=lambda step: step.build.getProperty('name') is None and
                     step.build.getProperty('nameInitMode') is None or
                     step.build.getProperty('nameInitMode') == NameInitOptions.GENERATE,
            hideStepIf=lambda results, s: results == SKIPPED
        )
    ]


def assignWorker(_builder, workerForBuilderList, buildRequest):
    """
    Returns available worker for a builder
    filtered by the scheduler which triggered build and by the giver task-host mapping
    See 'nextWorker' at http://docs.buildbot.net/current/manual/configuration/builders.html
    """
    workerNames = workers.workersOnHosts(buildRequest.properties.getProperty("host", default=""),
                                         *buildRequest.properties.getProperty("buildHosts", default=[]))
    for workerForBuilder in workerForBuilderList:
        workerName = workerForBuilder.worker.workername
        if workerForBuilder.isAvailable() and workerName in workerNames:
            buildRequest.properties.setProperty("host", workers.workerToHostMap()[workerName],
                                                "Assign worker")
            return workerForBuilder


def assignBestHost(hostPool):

    def selectWorkersFromHostPool(builder, workersForBuilders, buildRequest):
        """
        Returns availble workersForBuilders on a host with the least tasks running
        :param builder: Builder for this task
        :param workersForBuilders: List of workerForBuilders
        :param buildRequest: build request
        :return: List of workersForBuilders for a specific host
        """
        # Proceed directly to worker assignment if host is specified
        if buildRequest.properties.getProperty("host"):
            return assignWorker(buildRequest, workersForBuilders, buildRequest)

        workerToHostMap = workers.workerToHostMap()
        hostToWorkersMap = {}
        for name, host in workerToHostMap.items():
            if host in hostPool or not hostPool:
                hostToWorkersMap[host] = hostToWorkersMap.get(host, []) + [name]
        workersForBuilders = list(filter(lambda wfb: workerToHostMap[wfb.worker.workername] in hostToWorkersMap,
                                         workersForBuilders))
        availableWFB = collectAvailableWorkers(workersForBuilders, workerToHostMap, hostToWorkersMap)
        return assignWorker(builder, availableWFB, buildRequest)

    return selectWorkersFromHostPool


def findBestHost(workersForBuilders, workerToHostMap, hostToWorkersMap):
    """
    Finds host with least amount of tasks running on a builder
    :param workersForBuilders: List of workerForBuilders
    :param workerToHostMap: Map where each worker contains its host
    :param hostToWorkersMap: Map where each host contains its workers
    :return: Name of hosts
    """
    occupiedWorkers = dict(map(lambda item: (item[0], len(item[1])), hostToWorkersMap.items()))
    for wfb in workersForBuilders:
        if wfb.isAvailable():
            occupiedWorkers[workerToHostMap[wfb.worker.workername]] -= 1
    bestHost = sorted(occupiedWorkers.items(), key=lambda item: item[1])[0]
    return bestHost[0]


def collectAvailableWorkers(workersForBuilders, workerToHostMap, hostToWorkersMap):
    """
    Collects available workers from the least loaded host
    :param workersForBuilders: List of workerForBuilders
    :param workerToHostMap: Map where each worker contains its host
    :param hostToWorkersMap: Map where each host contains its workers
    :return: List of available workers on the best host
    """
    availableWFB = []
    bestHost = findBestHost(workersForBuilders, workerToHostMap, hostToWorkersMap)
    for wfb in workersForBuilders:
        if wfb.worker.workername in hostToWorkersMap[bestHost]:
            availableWFB.append(wfb)
    return availableWFB


def generateRepositories():
    """
    Runs 'mdbcu generate-product-repositories' command on a worker
    :return: list of steps
    """
    return [steps.ShellCommand(
        name="Generate product repositories",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/mdbci"), "generate-product-repositories"],
        haltOnFailure=True
    )]


def syncRepod():
    """
    Creates steps for running rsync to remote workers
    :return: list of steps
    """
    return [RsyncShellSequence(name="Synchronizing ~/.config/mdbci/repo.d among workers",
                               haltOnFailure=False, flunkOnFailure=False, flunkOnWarnings=False)]


class RsyncShellSequence(ShellSequence):
    """
    rsync ~/.config/mdbci/repo.d directory from current worker
    to every other unique worker's host
    """
    def createRsyncSequence(self, hosts):
        """
        Creates a list of shell commands for synchronization of .config directory on each given host
        :param hosts: List of host addresses
        :return: List with rsync shell command for each host
        """
        return [util.ShellArg(command="rsync -r ~/.config/mdbci/repo.d/ -e "
                                      "'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' "
                                      "{}@{}:~/.config/mdbci/repo.d".format(constants.HOST_USERS.get(host), constants.HOST_FULL.get(host)),
                              logfile="rsync to {}".format(host)) for host in hosts]

    def getRemoteWorkersHosts(self):
        """
        Creates a list of unique hosts which holds running workers excluding host of the current worker
        :return: List of host addresses
        """
        hosts = set()
        currentHost = None
        for worker in workers.WORKER_CREDENTIALS:
            if worker["name"] != self.getProperty("workername"):
                if self.master.workers.connections.get(worker["name"]):
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


def downloadScript(scriptName, hideStepIf=True, **kwargs):
    """Downloads script with the given name from scripts directory to the current worker"""
    return [steps.FileDownload(
        name="Transferring {} to worker".format(scriptName),
        mastersrc="maxscale/builders/support/scripts/{}".format(scriptName),
        workerdest=util.Interpolate("%(prop:builddir)s/scripts/{}".format(scriptName)),
        mode=0o755,
        hideStepIf=hideStepIf,
        **kwargs
    )]


def remoteParseCtestLogAndStoreIt():
    """Parse ctest results and store them in the LOGS directory"""
    def remote():
        buildId = "{}-{}".format(buildername, buildnumber)
        outputDirectory = os.path.join(builddir, buildId, "ctest_sublogs")
        subprocess.run(["{}/scripts/parse_ctest_log.py".format(builddir),
                        buildLogFile,
                        "-o", os.path.join(builddir, "results_{}".format(buildnumber)),
                        "-r", "-f",
                        "-j", jsonResultsFile,
                        "-s", outputDirectory])

        storeDirectory = os.path.join(HOME, "LOGS", buildId, "LOGS")
        for logDirectory in os.listdir(outputDirectory):
            targetDirectory = os.path.join(storeDirectory, logDirectory)
            os.umask(0o002)
            os.makedirs(targetDirectory, exist_ok=True)
            shutil.copy(os.path.join(outputDirectory, logDirectory, "ctest_sublog"), targetDirectory)

    return support.executePythonScript(
        "Parse ctest results log and save it to logs directory",
        remote, alwaysRun=True)


def writeBuildResultsToDatabase(**kwargs):
    """Call the script to save results to the database"""
    return [steps.SetPropertyFromCommand(
        name="Save test results to the database",
        command=[util.Interpolate("%(prop:builddir)s/scripts/write_build_results.py"),
                 util.Property("jsonResultsFile")],
        extract_fn=extractDatabaseBuildid,
        **kwargs)]


def extractDatabaseBuildid(rc, stdout, stderr):
    keyPhrase = "LAST_WRITE_BUILD_RESULTS_ID"
    for line in stdout.split("\n"):
        if line.startswith(keyPhrase):
            return {keyPhrase: line[len(keyPhrase) + 2:]}
    return {}


def remoteRunScriptAndLog(scriptName, logFile, resultFile, **kwargs):
    """
    Runs shell script which name is given in a property script_name
    and save results to the log file
    """
    service_script = "run_script_and_log.py"
    actions = downloadScript(service_script)
    actions.append(
        steps.ShellCommand(command=[
            util.Interpolate("%(prop:builddir)s/scripts/{script}".format(script=service_script)),
            "--script_name", scriptName,
            "--log_file", logFile,
            "--result_file", resultFile],
            timeout=1800,
            **kwargs)
    )
    return actions


def parseCtestLog():
    """Downloads and runs ctect log parser"""
    return downloadScript("parse_ctest_log.py", alwaysRun=True) + remoteParseCtestLogAndStoreIt()


def writeBuildsResults():
    """Downloads and runs script for saving build results to database"""
    return downloadScript("write_build_results.py", alwaysRun=True) + writeBuildResultsToDatabase(alwaysRun=True)


def downloadAndRunScript(scriptName, args=(), **kwargs):
    """
    Downloads the script to remote location and executes it
    :param: scriptName name of the local script to execute
    """
    remoteScriptName = util.Interpolate("%(prop:builddir)s/scripts/{}".format(scriptName))
    downloadStep = steps.FileDownload(
        name="Transferring {} to worker".format(scriptName),
        mastersrc="maxscale/builders/support/scripts/{}".format(scriptName),
        workerdest=remoteScriptName,
        hideStepIf=True,
        mode=0o755
    )
    executeStep = steps.ShellCommand(
        command=[remoteScriptName, *args],
        timeout=1800,
        **kwargs
    )
    return [downloadStep, executeStep]


@util.renderer
def renderTestSet(properties):
    """
    Returns test set value if it's present, otherwise returns test set filtered by branch
    :param properties:
    :return: Test set
    """
    return properties.getProperty("test_set") \
        or get_test_set_by_branch(properties.getProperty('branch'))


class BuildAllTrigger(Trigger):
    """
    Implements custom trigger step which triggers task on a virtual builder for every marked checkbox
    """
    def getSchedulersAndProperties(self):
        """
        Overrides method getSchedulersAndProperties of Trigger class
        so that it returns a scheduler for every marked checkbox
        :return: List which contains schedulers for every marked checkbox
        """
        schedulers = []
        for checkboxName, checkboxValue in self.set_properties["build_box_checkbox_container"].items():
            if checkboxValue:
                propertiesToSet = {}
                propertiesToSet.update(self.set_properties)
                propertiesToSet.update({"box": checkboxName})
                propertiesToSet.update({"virtual_builder_name":
                                        "{}_{}".format(self.set_properties["virtual_builder_name"], checkboxName)})
                for schedulerName in self.schedulerNames:
                    schedulers.append({
                        "sched_name": schedulerName,
                        "props_to_set": propertiesToSet,
                        "unimportant": schedulerName in self.unimportantSchedulerNames
                    })

        return schedulers


def runSshCommand(name='', host="", command=(), timeout=1800, **kwargs):
    """
    Run command on the remote server
    :param name: name of the command to show to end user
    :param host: the host definition
    :param command: a set of separate command parts
    :param timeout:
    :param kwargs: different arguments to pass to ShellCommand
    :return: ShellCommand configured to run remote ssh command
    """
    sshCommand = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", host]
    sshCommand.extend(command)
    return steps.ShellCommand(
        name=name,
        command=sshCommand,
        timeout=timeout,
        **kwargs
    )


def rsyncViaSsh(name="", local="", remote="", timeout=1800, **kwargs):
    """
    Run rsync to put directory to the remote server
    :param name: Command name
    :param local: path to the local folder
    :param remote: path to the remote folder that
    :param timeout: timeout for the service
    :param kwargs: misc arguments to ShellCommand
    :return: ShellCommand configured to run rsync remote ssh
    """
    rsyncCommand = ["rsync", "-avz", "--progress", "-e",
                    "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null", local, remote]
    return steps.ShellCommand(
        name=name,
        command=rsyncCommand,
        timeout=timeout,
        **kwargs
    )
