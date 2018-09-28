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
}


@util.renderer
def configureCommonProperties(properties):
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
    }

def showTestResult(**kwargs):
    return common.StdoutShellCommand(
        name="test_result",
        collectStdout=True,
        command=util.Interpolate(r"cat %(prop:builddir)s/results_%(prop:buildnumber)s "
                                 r"%(prop:builddir)s/coredumps_%(prop:buildnumber)s "
                                 r"| sed -E 's/\\n\\//g'"),
        **kwargs)


def RunPerformanceTest()
    return os.system(
        util.Interpolate(
            "cd ~/maxscale-performance-test/; \
             unset COMP_WORDBREAKS; \
             ./bin/performance_test -v \
             --server-config=~/performance_test_servers/performance-test_network_config \
             --remote-test-app tests/run_sysbench.sh \
             --db-server-2-config slave-config.sql.erb \
             --db-server-3-config slave-config.sql.erb \
             --db-server-4-config slave-config.sql.erb \
             --mariadb-version %(prop:version)s \
             --maxscale-config base.cnf.erb \
             --maxscale-version %(prop:target)s \
             --keep-servers true \
             > %(prop:builddir)s/results_%(prop:buildnumber)s \
             "
          )
     )


def createRunTestSteps():
    testSteps = []
    testSteps.extend(common.configureMdbciVmPathProperty())
    testSteps.append(steps.SetProperties(properties=configureCommonProperties))
    testSteps.append(RunPerformanceTest())
    testSteps.append(showTestResult(alwaysRun=True))
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
        tags=["perfirmance_test"],
        env=ENVIRONMENT,
    )
]
