import datetime
from collections import defaultdict
from buildbot.plugins import util, steps
from buildbot.process.buildstep import ShellMixin
from buildbot.process.results import SKIPPED
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shellsequence import ShellSequence
from twisted.internet import defer
from maxscale.builders.support import support
from maxscale.change_source.maxscale import get_test_set_by_branch
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
    """
    Creates renderer which return formatted datetime
    :param format: format of datetime string
    :return: rendered for datetime
    """
    @util.renderer
    def formatDateTime(properties):
        return datetime.datetime.now().strftime(format)

    return formatDateTime


def setMissingTarget():
    """
    Sets 'target' property of the build to <branch>-buildbot-<starttime> if it isn't set yet
    :return: list of steps
    """
    return [steps.SetProperty(
        name=util.Interpolate("Set 'target' property"),
        property="target",
        value=util.Interpolate("%(prop:branch)s-buildbot-%(kw:startTime)s",
                               startTime=getFormattedDateTime("%b%d-%H:%M:%S")),
        doStepIf=lambda step: step.build.getProperty('target') is None,
        hideStepIf=lambda results, s: results == SKIPPED
    )]


def assignBuildRequest(builder, buildRequestQueue):
    """
    Chooses first request from the build request queue that can be run on any available worker
    :param builder: Builder of the requested build
    :param buildRequestQueue: List of pending build requests
    :return: Build request that can start a build
    """
    workerToHostMap = workers.workerToHostMap()
    availableWorkers = defaultdict(list)
    for wfb in builder.workers:
        if wfb.isAvailable():
            availableWorkers[workerToHostMap[wfb.worker.workername]].append(wfb.worker.workername)

    for buildRequest in buildRequestQueue:
        host = buildRequest.properties.getProperty("host")
        if availableWorkers.get(host) or not host:
            return buildRequest


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
        return [util.ShellArg(command="rsync -r ~/.config/mdbci/repo.d/ "
                                      "vagrant@{}.mariadb.com:~/.config/mdbci/repo.d".format(host),
                              logfile="rsync to {}.mariadb.com".format(host)) for host in hosts]

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


def downloadScript(scriptName, **kwargs):
    """Downloads script with the given name from scripts directory to the current worker"""
    return [steps.FileDownload(
        name="Transferring {} to worker".format(scriptName),
        mastersrc="maxscale/builders/support/scripts/{}".format(scriptName),
        workerdest=util.Interpolate("%(prop:builddir)s/scripts/{}".format(scriptName)),
        mode=0o755,
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


def remoteStoreCoredumps():
    """Find the coredumps and store them in the LOGS directory"""
    def remote():
        result = subprocess.check_output(
            ["{}/scripts/coredump_finder.py".format(builddir),
             "{}-{}".format(buildername, buildnumber), "url"])
        coredumpLogFile = open(os.path.join(builddir, "coredumps_{}".format(buildnumber)), "w")
        coredumpLogFile.write("COREDUMPS \\\n")
        if result == "":
            coredumpLogFile.write("Coredumps were not found for build {}".format(buildnumber))
        else:
            for dump in result.decode("utf_8").split("\n"):
                coredumpLogFile.write("{} \\\n".format(dump))
        buildId = "{}-{}".format(buildername, buildnumber)
        shutil.copy(buildLogFile, os.path.join(HOME, "LOGS", buildId))

    return support.executePythonScript(
        "Find and store coredumps", remote, alwaysRun=True)


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


def showTestResult(**kwargs):
    """
    Stores results of a test run into the buildbot's database
    for retrieving later during email composition
    :param kwargs:
    :return:
    """
    return [StdoutShellCommand(
        name="test_result",
        collectStdout=True,
        command=util.Interpolate(r"cat %(prop:builddir)s/results_%(prop:buildnumber)s "
                                 r"%(prop:builddir)s/coredumps_%(prop:buildnumber)s "
                                 r"| sed -E 's/\\n\\//g'"),
        **kwargs)]


def remoteRunScriptAndLog():
    """
    Runs shell script which name is given in a property 'script_name' of a builder on a worker
    and save results to the log file
    """
    def remote():
        if not os.path.exists("maxscale-system-test/mdbci"):
            os.mkdir("default-maxscale-branch")
            subprocess.run(["git", "clone", repository, "default-maxscale-branch/MaxScale"])
            shutil.copytree("default-maxscale-branch/MaxScale/maxscale-system-test/mdbci", "maxscale-system-test")

        logFile = open(buildLogFile, "w")
        process = subprocess.Popen(["maxscale-system-test/mdbci/{}".format(script_name)],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for byteLine in process.stdout:
            line = byteLine.decode("utf-8", "replace")
            sys.stdout.write(line)
            sys.stdout.flush()
            logFile.write(line)
        process.wait()
        logFile.close()

        testLogFile = open(resultFile, "w")
        testLogFile.write(str(process.returncode))
        testLogFile.close()
        sys.exit(process.returncode)

    return support.executePythonScript(
        "Run MaxScale tests using MDBCI", remote)


def parseCtestLog():
    """Downloads and runs ctect log parser"""
    return downloadScript("parse_ctest_log.py", alwaysRun=True) + remoteParseCtestLogAndStoreIt()


def writeBuildsResults():
    """Downloads and runs script for saving build results to database"""
    return downloadScript("write_build_results.py", alwaysRun=True) + writeBuildResultsToDatabase(alwaysRun=True)


def findCoredump():
    """Downloads and runs coredump finder"""
    return downloadScript("coredump_finder.py", alwaysRun=True) + remoteStoreCoredumps()


@util.renderer
def renderTestSet(properties):
    """
    Returns test set value if it's present, otherwise returns test set filtered by branch
    :param properties:
    :return: Test set
    """
    return properties.getProperty("test_set") \
        or get_test_set_by_branch(properties.getProperty('branch'))
