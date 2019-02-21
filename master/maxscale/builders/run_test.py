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
    "no_vm_revert": util.Property("no_vm_revert"),
    "template": util.Property("template"),
    "config_to_clone": util.Property("config_to_clone"),
    "test_branch": util.Property("branch"),
    "use_valgrind": util.Property("use_valgrind"),
}


@util.renderer
def configureCommonProperties(properties):
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
        "mdbciConfig": util.Interpolate("%(prop:MDBCI_VM_PATH)s/%(prop:name)s")
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
    testSteps.extend(common.remoteRunScriptAndLog())
    testSteps.extend(common.parseCtestLog())
    testSteps.extend(common.findCoredump())
    testSteps.extend(common.writeBuildsResults())
    testSteps.extend(common.showTestResult(alwaysRun=True))
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
        nextBuild=common.assignBuildRequest,
        factory=createTestFactory(),
        tags=["test"],
        env=ENVIRONMENT,
        properties={"script_name": "run_test.sh"},
        defaultProperties={
            "try_already_running": None
        })
]
