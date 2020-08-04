import os
from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from maxscale.builders.support import common, support
from buildbot.process.results import SUCCESS, SKIPPED
from maxscale import workers


ENVIRONMENT = {
    "WORKSPACE": util.Interpolate('%(prop:builddir)s/build'),
    "JOB_NAME": util.Property("buildername"),
    "BUILD_NUMBER": util.Interpolate("%(prop:buildnumber)s"),
    "BUILD_TIMESTAMP": util.Interpolate('%(kw:datetime)s',
                                        datetime=common.getFormattedDateTime("%Y-%m-%d %H-%M-%S")),
    "target": util.Property("target"),
    "version": util.Property("version"),
    "maxscale_threads": util.Property("maxscale_threads"),
    "sysbench_threads": util.Property("sysbench_threads"),
    "perf_runtime": util.Interpolate("%(prop:perf_runtime)s"),
    "perf_port": util.Property("perf_port"),
    "use_callgrind": util.Property("use_callgrind"),
}


@util.renderer
def configureCommonProperties(properties):
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
        "networkConfigPath": '.config/performance_test/performance-test_network_config'
    }


def parsePerformanceTestResults(**kwargs):
    return steps.ShellCommand(
        name="Parsing performance tests results",
        command=util.Interpolate(
            "~/mdbci/scripts/benchmark_parser/parse_log.rb \
            -i %(prop:builddir)s/results_%(prop:buildnumber)s \
            -e %(prop:builddir)s/env_%(prop:buildnumber)s \
            -o %(prop:builddir)s/json_%(prop:buildnumber)s \
             "),
        **kwargs)


def writePerformanceTestResults(**kwargs):
    return steps.ShellCommand(
        name="Writing performance tests results to DB",
        command=util.Interpolate(
            "~/mdbci/scripts/benchmark_parser/write_benchmark_results.rb \
            -i %(prop:builddir)s/json_%(prop:buildnumber)s \
            -e %(prop:builddir)s/env_%(prop:buildnumber)s \
             "),
        **kwargs)


def createRunTestSteps():
    testSteps = []
    testSteps.extend(common.configureMdbciVmPathProperty())
    testSteps.append(steps.SetProperties(properties=configureCommonProperties))
    testSteps.extend(common.downloadAndRunScript(
        name="Run performance tests",
        scriptName="run_performance_test.py",
        args=[
            "--build_dir", util.Property("builddir"),
            "--build_number", util.Property("buildnumber"),
            "--network_config_path", util.Property("networkConfigPath"),
            "--version", util.Property("version"),
            "--perf_cnf_template", util.Property("perf_cnf_template"),
            "--target", util.Property("target")
        ]
    ))
    testSteps.append(parsePerformanceTestResults(alwaysRun=True))
    testSteps.append(writePerformanceTestResults(alwaysRun=True))
    testSteps.extend(common.cleanBuildDir())
    return testSteps


def createTestFactory():
    factory = util.BuildFactory()
    testSteps = createRunTestSteps()
    factory.addSteps(testSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="run_performance_test",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=createTestFactory(),
        tags=["performance_test"],
        env=ENVIRONMENT,
    )
]
