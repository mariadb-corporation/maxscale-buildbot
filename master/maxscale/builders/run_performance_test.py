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
}


@util.renderer
def configureCommonProperties(properties):
    return {
        "buildLogFile": util.Interpolate("%(prop:builddir)s/build_log_%(prop:buildnumber)s"),
        "resultFile": util.Interpolate("result_%(prop:buildnumber)s"),
        "jsonResultsFile": util.Interpolate("%(prop:builddir)s/json_%(prop:buildnumber)s"),
        "networkConfigPath": '.config/performance_test/performance-test_network_config'
    }


def testConnecton():
    """
    Tests if nodes specified in performance-test_network_config are available
    :return:
    """

    def remoteCode():
        import re
        with open('{}/{}'.format(os.environ['HOME'], networkConfigPath), encoding="UTF-8") as configFile:
            networkConfig = {}
            configRegexp = re.compile(r'^(\S+)_(network|whoami|keyfile)=(\S+)$')
            for line in configFile:
                if configRegexp.match(line):
                    match = configRegexp.search(line)
                    if match.group(1) not in networkConfig:
                        networkConfig[match.group(1)] = {}
                    networkConfig[match.group(1)].update({match.group(2): match.group(3)})

            for node, config in networkConfig.items():
                host = '{}@{}'.format(config['whoami'], config['network'])
                result = subprocess.call('ssh -i {} -o ConnectTimeout=10 {} exit'
                                         .format(config['keyfile'], host), shell=True)
                if result:
                    sys.exit(subprocess.call('sudo $HOME/restart_vpn.sh', shell=True))

        sys.exit(0)

    return support.executePythonScript('Testing connection to the remote machine', remoteCode)


def runPerformanceTest():

    def remoteCode():
        os.chdir('{}/maxscale-performance-test/'.format(os.environ['HOME']))
        if 'COMP_WORDBREAKS' in os.environ:
            del os.environ['COMP_WORDBREAKS']

        logFile = open('{}/results_{}'.format(builddir, buildnumber), 'w')
        process = subprocess.Popen(['./bin/performance_test', '-v',
                                    '--server-config', '{}/{}'.format(os.environ['HOME'], networkConfigPath),
                                    '--remote-test-app',
                                    '{}/.config/performance_test/run_sysbench.sh'.format(os.environ['HOME']),
                                    '--db-server-2-config', 'slave-config.sql.erb',
                                    '--db-server-3-config', 'slave-config.sql.erb',
                                    '--db-server-4-config', 'slave-config.sql.erb',
                                    '--mariadb-version', version,
                                    '--maxscale-config', perf_cnf_template,
                                    '--maxscale-version', target,
                                    '--keep-servers', 'true'],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for byteLine in process.stdout:
            line = byteLine.decode("utf-8", "replace")
            sys.stdout.write(line)
            logFile.write(line)
        process.wait()
        logFile.close()
        sys.exit(process.returncode)

    return support.executePythonScript('Run performance tests', remoteCode)


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
    testSteps.extend(testConnecton())
    testSteps.extend(runPerformanceTest())
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
        nextBuild=common.assignBuildRequest,
        factory=createTestFactory(),
        tags=["performance_test"],
        env=ENVIRONMENT,
    )
]
