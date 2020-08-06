from buildbot.config import BuilderConfig
from buildbot.plugins import steps, util
from .support import common
from maxscale import workers
from maxscale.config import constants

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
    "no_vm_revert": util.Property("no_vm_revert"),
    "template": util.Property("template"),
    "config_to_clone": util.Property("config_to_clone"),
    "test_branch": util.Property("branch"),
    "use_valgrind": util.Property("use_valgrind"),
    "use_callgrind": util.Property("use_callgrind"),
}


@util.renderer
def configureCommonProperties(properties):
    testId = "{}-{}".format(properties.getProperty("buildername"), properties.getProperty("buildnumber"))
    logDirectory = "{}/LOGS/{}/".format(properties.getProperty("HOME"), testId)
    coreDumpsLog = "{}/coredumps_{}".format(logDirectory, testId)
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
        "mdbciConfig": util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:name)s"),
        "upload_server": constants.UPLOAD_SERVERS[properties.getProperty("host")],
        "testId": testId,
        "logDirectory": logDirectory,
        "coreDumpsLog": coreDumpsLog,
        "mdbciVMPath": util.Interpolate("%(prop:name)s_vms"),
    }


def createTestFactory():
    factory = util.BuildFactory()
    factory.addSteps(common.configureMdbciVmPathProperty())
    factory.addStep(common.determineBuildId())
    factory.addStep(common.determineTestRunName())
    factory.addStep(steps.SetProperties(
        name="Configure build properties",
        properties=configureCommonProperties,
    ))
    factory.addSteps(common.cloneRepository())
    factory.addStep(common.generateMdbciRepositoryForTarget())
    factory.addSteps(common.remoteRunScriptAndLog(
        name="Run MaxScale tests",
        scriptName="run_test_vm.sh",
        logFile=util.Property("buildLogFile"),
        resultFile=util.Property("resultFile"),
    ))
    factory.addSteps(common.downloadAndRunScript(
        name="Parse ctest results log and save it to logs directory",
        scriptName="parse_ctest_log.py",
        args=[
            util.Property("buildLogFile"),
            "--output-log-file", util.Interpolate("%(prop:builddir)s/results_%(prop:buildnumber)s"),
            "--human-readable", "--only-failed",
            "--output-log-json-file", util.Property("jsonResultsFile"),
            "--ctest-sublogs-path", util.Interpolate("%(prop:builddir)s/%(prop:buildername)s-%(prop:buildnumber)s/ctest_sublogs"),
            "--store-directory", util.Interpolate("%(prop:HOME)s/LOGS/results_%(prop:buildnumber)s/LOGS")
        ],
        alwaysRun=True
    ))
    factory.addSteps(common.downloadAndRunScript(
        name="Find core dumps and record information into the file",
        scriptName="coredump_finder.py",
        args=[
            "--directory", util.Property("logDirectory"),
            "--remote-prefix", util.Interpolate("%(kw:server)s%(prop:testId)s/",
                                                server=constants.CI_SERVER_LOGS_URL),
            "--output-file", util.Property("coreDumpsLog"),
        ],
        haltOnFailure=False,
        flunkOnFailure=False,
        alwaysRun=True
    ))
    factory.addSteps(common.writeBuildsResults())
    factory.addStep(
        common.StdoutShellCommand(
            name="test_result",
            command=util.Interpolate("cat %(prop:builddir)s/results_%(prop:buildnumber)s %(prop:coreDumpsLog)s"),
            alwaysRun=True)
    )
    factory.addStep(common.rsyncViaSsh(
        name="Rsync test logs to the logs server",
        local=util.Property("logDirectory"),
        remote=util.Interpolate(
            "%(prop:upload_server)s:/srv/repository/bb-logs/Maxscale/%(prop:testId)s/"),
        alwaysRun=True,
        flunkOnFailure=False,
    ))
    factory.addStep(common.runSshCommand(
        name="Fix permissions on remote server",
        host=util.Property("upload_server"),
        command=["chmod", "777", "-R",
                 util.Interpolate("/srv/repository/bb-logs/Maxscale/%(prop:testId)s/")],
        alwaysRun=True,
        flunkOnFailure=False,
    ))
    factory.addStep(steps.ShellCommand(
        name="Remove logs from worker host",
        command=["rm", "-rf", util.Property("logDirectory")],
        alwaysRun=True,
    ))
    factory.addSteps(common.destroyAllConfigurations(util.Interpolate("%(prop:HOME)s/%(prop:name)s_vms")))
    factory.addSteps(common.cleanBuildDir())
    return factory


BUILDERS = [
    BuilderConfig(
        name="run_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=createTestFactory(),
        tags=["test"],
        env=ENVIRONMENT,
        defaultProperties={
            "try_already_running": None
        })
]
