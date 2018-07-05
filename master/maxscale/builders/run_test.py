from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from . import common, support
from maxscale import workers


ENVIRONMENT = {
    "JOB_NAME": util.Property("buildername"),
    "BUILD_NUMBER": util.Interpolate("%(prop:buildnumber)s"),
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
    "logs_dir": util.Interpolate("%(prop:HOME)s/logs_dir"),
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


def remoteRunTestAndLog():
    """Run tests and save results to the log file"""
    if not os.path.exists("maxscale-system-test/mdbci"):
        os.mkdir("default-maxscale-branch")
        subprocess.run(["git", "clone", repository, "default-maxscale-branch/MaxScale"])
        shutil.copytree("default-maxscale-branch/MaxScale/maxscale-system-test/mdbci", "maxscale-system-test")

    logFile = open(buildLogFile, "w")
    process = subprocess.Popen(["maxscale-system-test/mdbci/run_test.sh"], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
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
    subprocess.run([os.path.join(HOME, "/mdbci/scripts/build_parser/parse_ctest_log.rb"),
                    "-l", buildLogFile,
                    "-o", os.path.join(builddir, "results_{}".format(buildnumber)),
                    "-r", "-f",
                    "-j", jsonResultsFile,
                    "-s", outputDirectory])

    storeDirectory = os.path.join(HOME, "LOGS", buildId, "LOGS")
    for logDirectory in os.listdir(outputDirectory):
        targetDirectory = os.path.join(storeDirectory, logDirectory)
        os.makedirs(targetDirectory, exist_ok=True)
        shutil.copy(os.path.join(outputDirectory, logDirectory, "ctest_sublog"), targetDirectory)


def remoteStoreCoredumps():
    """Find the coredumps and store them in the LOGS directory"""
    result = subprocess.check_output(
        [os.path.join(HOME, "/mdbci/scripts/build_parser/coredump_finder.sh"),
         "{}-{}".format(buildername, buildnumber), "url"])
    coredumpLogFile = open(os.path.join(builddir, "coredumps_{}".format(buildnumber)), "w")
    coredumpLogFile.write("COREDUMPS \\\n")
    if result == "":
        coredumpLogFile.write("Coredumps were not found for build {}".format(buildnumber))
    else:
        for dump in result.split("\n"):
            coredumpLogFile.write("{} \\\n".format(dump))
    buildId = "{}-{}".format(buildername, buildnumber)
    shutil.copy(buildLogFile, os.path.join(HOME, "LOGS", buildId))


def writeBuildResultsToDatabase():
    """Call the script to save results to the database"""
    return steps.ShellCommand(
        name="Save test results to the database",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/scripts/build_parser/write_build_results.rb"),
                 "-f", util.Property("jsonResultsFile")])


def uploadTestRunsToReportPortal():
    """Save test results to the report portal"""
    return steps.ShellCommand(
        name="Send test results to the Report Portal",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/scripts/build_parser/report_portal/bin/upload_testrun.rb"),
                 util.Property("jsonResultsFile"),
                 util.Interpolate("%(prop:HOME)s/report-portal-config.yml")])


def createRunTestSteps():
    testSteps = []
    testSteps.extend(common.configureMdbciVmPathProperty())
    testSteps.extend(common.cloneRepository())
    testSteps.append(steps.SetProperties(properties=configureCommonProperties))
    testSteps.extend(support.executePythonScript(
        "Run MaxScale tests using MDBCI", remoteRunTestAndLog))
    testSteps.extend(support.executePythonScript(
        "Parse ctest results log and save it to logs directory", remoteParseCtestLogAndStoreIt))
    testSteps.append(writeBuildResultsToDatabase())
    testSteps.append(uploadTestRunsToReportPortal())
    testSteps.extend(common.destroyVirtualMachine())
    testSteps.extend(common.removeLock())
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
        factory=createTestFactory(),
        tags=["test"],
        env=ENVIRONMENT)
]
