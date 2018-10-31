import os
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
    "target": util.Property("target"),
    "version": util.Property("version"),
    "maxscale_threads": util.Property("maxscale_threads"),
    "sysbench_threads": util.Property("sysbench_threads"),
}


@util.renderer
def configureCommonProperties(properties):
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
    }


def runPerformanceTest(**kwargs):
    return steps.ShellCommand(
        name="Run performance tests",
        command=util.Interpolate(
            "cd ~/maxscale-performance-test/; \
             unset COMP_WORDBREAKS; \
             ./bin/performance_test -v \
             --server-config=~/.config/performance_test/performance-test_network_config \
             --remote-test-app tests/run_sysbench.sh \
             --db-server-2-config slave-config.sql.erb \
             --db-server-3-config slave-config.sql.erb \
             --db-server-4-config slave-config.sql.erb \
             --mariadb-version %(prop:version)s \
             --maxscale-config base.cnf.erb \
             --maxscale-version %(prop:target)s \
             --keep-servers true \
             > %(prop:builddir)s/results_%(prop:buildnumber)s \
             "),
        **kwargs)


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
    testSteps.append(runPerformanceTest(alwaysRun=True))
    testSteps.append(parsePerformanceTestResults(alwaysRun=True))
    testSteps.append(writePerformanceTestResults(alwaysRun=True))
    testSteps.extend(common.showTestResult(alwaysRun=True))
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
