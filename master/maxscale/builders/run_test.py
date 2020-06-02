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
        "upload_server" : constants.UPLOAD_SERVERS[properties.getProperty("host")],
    }


def uploadTestRunsToReportPortal(**kwargs):
    """Save test results to the report portal"""
    return steps.ShellCommand(
        name="Send test results to the Report Portal",
        command=[util.Interpolate("%(prop:HOME)s/mdbci/scripts/build_parser/report_portal/bin/upload_testrun.rb"),
                 util.Property("jsonResultsFile"),
                 util.Interpolate("%(prop:HOME)s/report-portal-config.yml")],
        env={"LAST_WRITE_BUILD_RESULTS_ID": util.Property("LAST_WRITE_BUILD_RESULTS_ID")},
        **kwargs)


def createRunTestSteps():
    testSteps = []
    testSteps.extend(common.configureMdbciVmPathProperty())
    testSteps.extend(common.cloneRepository())
    testSteps.append(steps.SetProperties(properties=configureCommonProperties))
    cmd = '~/mdbci/mdbci generate-product-repositories --product maxscale_ci --product-version %(prop:target)s'
    testSteps.append(steps.ShellCommand(
        name="Generate new repo descriptions",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
    ))
    testSteps.extend(common.remoteRunScriptAndLog(name="Run MaxScale tests"))
    testSteps.extend(common.parseCtestLog())
    testSteps.extend(common.findCoredump())
    testSteps.extend(common.writeBuildsResults())
    testSteps.extend(common.showTestResult(alwaysRun=True))
    cmd = 'rsync -avz --progress -e ssh ~/LOGS/run_test-%(prop:buildnumber)s/ %(prop:upload_server)s:/srv/repository/bb-logs/Maxscale/run_test-%(prop:buildnumber)s/'
    testSteps.append(steps.ShellCommand(
        name="Rsync test logs to the logs server",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
        flunkOnFailure=False,
    ))
    cmd = 'rm -rf ~/LOGS/run_test-%(prop:buildnumber)s'
    testSteps.append(steps.ShellCommand(
        name="removes logs from worker host",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
        flunkOnFailure=False,
    ))
    cmd = 'ssh %(prop:upload_server)s chmod 777 -R /srv/repository/bb-logs/Maxscale/run_test-%(prop:buildnumber)s/'
    testSteps.append(steps.ShellCommand(
        name="Rsync test logs to the logs server",
        command=['/bin/bash', '-c', util.Interpolate(cmd)],
        timeout=1800,
        flunkOnFailure=False,
    ))
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
        properties={
            "scriptName": "run_test.sh"
        },
        defaultProperties={
            "try_already_running": None
        })
]
