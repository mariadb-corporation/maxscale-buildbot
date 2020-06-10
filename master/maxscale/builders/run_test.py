from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from maxscale.builders.support import common, support
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
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
        "mdbciConfig": util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:name)s"),
        "upload_server": constants.UPLOAD_SERVERS[properties.getProperty("host")],
        "buildId": util.Interpolate("%(prop:buildername)s-%(prop:buildnumber)s"),
        "logDirectory": util.Interpolate("%(prop:HOME)s/LOGS/%(prop:buildId)s/"),
        "coreDumpsLog": util.Interpolate("%(prop:HOME)s/LOGS/%(prop:buildId)s/coredumps_%(prop:buildId)s"),
    }


def createRunTestSteps():
    testSteps = []
    testSteps.extend(common.configureMdbciVmPathProperty())
    testSteps.extend(common.cloneRepository())
    testSteps.append(steps.SetProperties(properties=configureCommonProperties))
    testSteps.append(common.generateMdbciRepositoryForTarget())
    testSteps.extend(common.remoteRunScriptAndLog(
        name="Run MaxScale tests",
        scriptName="run_test.sh",
        logFile=util.Property("buildLogFile"),
        resultFile=util.Property("resultFile"),
    ))
    testSteps.extend(common.parseCtestLog())
    testSteps.extend(common.downloadAndRunScript(
        name="Find core dumps and record information into the file",
        scriptName="coredump_finder.py",
        args=[
            "--directory", util.Property("logDirectory"),
            "--remote-prefix", util.Interpolate("%(kw:server)s%(prop:buildId)s/",
                                                server=constants.CI_SERVER_LOGS_URL),
            "--output-file", util.Property("coreDumpsLog"),
        ],
        haltOnFailure=False,
        flunkOnFailure=False,
        alwaysRun=True
    ))
    testSteps.extend(common.writeBuildsResults())
    testSteps.append(
        common.StdoutShellCommand(
            name="test_result",
            command=util.Interpolate(r"cat %(prop:builddir)s/results_%(prop:buildnumber)s "
                                     r"%(prop:coreDumpsLog)s "
                                     r"| sed -E 's/\\n\\//g'"),
            alwaysRun=True)
    )
    testSteps.append(common.rsyncViaSsh(
        name="Rsync test logs to the logs server",
        local=util.Property("logDirectory"),
        remote=util.Interpolate(
            "%(prop:upload_server)s:/srv/repository/bb-logs/Maxscale/%(prop:buildId)s/"),
        alwaysRun=True,
        flunkOnFailure=False,
    ))
    testSteps.append(common.runSshCommand(
        name="Fix permissions on remote server",
        host=util.Property("upload_server"),
        command=["chmod", "777", "-R",
                 util.Interpolate("/srv/repository/bb-logs/Maxscale/%(prop:buildId)s/")],
        alwaysRun=True,
        flunkOnFailure=False,
    ))
    testSteps.append(steps.ShellCommand(
        name="Remove logs from worker host",
        command=["rm", "-rf", util.Interpolate("%(prop:HOME)s/LOGS/%(prop:buildId)s")],
        alwaysRun=True,
    ))
    testSteps.extend(common.destroyVirtualMachine())
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
        defaultProperties={
            "try_already_running": None
        })
]
