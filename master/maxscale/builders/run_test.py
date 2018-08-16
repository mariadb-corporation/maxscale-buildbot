from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from maxscale.builders.support import common, support
from maxscale import workers


ENVIRONMENT = {
    "WORKSPACE": util.Interpolate('%(prop:builddir)s/build'),
    "JOB_NAME": util.Property("buildername"),
    "BUILD_NUMBER": util.Interpolate("%(prop:buildnumber)s"),
    "BUILD_TIMESTAMP": util.Interpolate('%(kw:datetime)s',
                                        datetime=common.getFormattedDateTime("%Y-%m-%d %H-%M-%S")),
    "name": util.Property("name"),
    "target": util.Property("target"),
    "box": util.Property("box"),
    "product": util.Property("product"),
    "version": util.Property("version"),
    "do_not_destroy_vm": util.Property("do_not_destroy_vm"),
    "test_set": util.Property("test_set"),
    "ci_url": util.Property("ci_url"),
    "smoke": util.Property("smoke"),
    "big": util.Property("big"),
    "backend_ssl": util.Property("backend_ssl"),
    "use_snapshots": util.Property("use_snapshots"),
    "logs_dir": util.Property('logs_dir'),
    "no_vm_revert": util.Property("no_vm_revert"),
    "template": util.Property("template"),
    "config_to_clone": util.Property("config_to_clone"),
    "test_branch": util.Property("branch"),
}


@util.renderer
def configureCommonProperties(properties):
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
        "mdbciConfig": util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:name)s")
    }


def remoteRunScriptAndLog():
    """
    Runs shell script which name is given in a property 'script_name' of a builder on a worker
    and save results to the log file
    """
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
        logFile.write(line)
    process.wait()
    logFile.close()

    testLogFile = open(resultFile, "w")
    testLogFile.write(str(process.returncode))
    testLogFile.close()
    sys.exit(process.returncode)


def remoteParseCtestLogAndStoreIt():
    """Parse ctest results and store them in the LOGS directory"""
    buildId = "{}-{}".format(buildername, buildnumber)
    outputDirectory = os.path.join(builddir, buildId, "ctest_sublogs")
    subprocess.run([os.path.join(HOME, "mdbci/scripts/build_parser/parse_ctest_log.rb"),
                    "-l", buildLogFile,
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


def remoteStoreCoredumps():
    """Find the coredumps and store them in the LOGS directory"""
    result = subprocess.check_output(
        [os.path.join(HOME, "mdbci/scripts/build_parser/coredump_finder.sh"),
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


def writeBuildResultsToDatabase(**kwargs):
    """Call the script to save results to the database"""
    return steps.ShellCommand(
        name="Save test results to the database",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/scripts/build_parser/write_build_results.rb"),
                 "-f", util.Property("jsonResultsFile")],
        **kwargs)


def uploadTestRunsToReportPortal(**kwargs):
    """Save test results to the report portal"""
    return steps.ShellCommand(
        name="Send test results to the Report Portal",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/scripts/build_parser/report_portal/bin/upload_testrun.rb"),
                 util.Property("jsonResultsFile"),
                 util.Interpolate("%(prop:HOME)s/report-portal-config.yml")],
        **kwargs)


def showTestResult(**kwargs):
    return common.StdoutShellCommand(
        name="test_result",
        collectStdout=True,
        command=util.Interpolate(r"cat %(prop:builddir)s/results_%(prop:buildnumber)s "
                                 r"%(prop:builddir)s/coredumps_%(prop:buildnumber)s "
                                 r"| sed -E 's/\\n\\//g'"),
        **kwargs)


def createRunTestSteps():
    testSteps = []
    testSteps.extend(common.configureMdbciVmPathProperty())
    testSteps.extend(common.cloneRepository())
    testSteps.append(steps.SetProperties(properties=configureCommonProperties))
    testSteps.extend(support.executePythonScript(
        "Run MaxScale tests using MDBCI", remoteRunScriptAndLog))
    testSteps.extend(support.executePythonScript(
        "Parse ctest results log and save it to logs directory",
        remoteParseCtestLogAndStoreIt, alwaysRun=True))
    testSteps.extend(support.executePythonScript(
        "Find and store coredumps", remoteStoreCoredumps, alwaysRun=True))
    testSteps.append(writeBuildResultsToDatabase(alwaysRun=True))
    testSteps.append(uploadTestRunsToReportPortal(alwaysRun=True))
    testSteps.append(showTestResult(alwaysRun=True))
    testSteps.extend(common.destroyVirtualMachine())
    testSteps.extend(common.removeLock())
    testSteps.extend(common.cleanBuildDir())
    return testSteps


def createTestFactory():
    factory = util.BuildFactory()
    testSteps = createRunTestSteps()
    factory.addSteps(testSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="run_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=createTestFactory(),
        tags=["test"],
        env=ENVIRONMENT,
        properties={"script_name": "run_test.sh"},
        defaultProperties={
            "try_already_running": None
        })
]
