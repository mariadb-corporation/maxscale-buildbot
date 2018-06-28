import os

from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from buildbot.process.buildstep import ShellMixin
from buildbot.steps import shell
from twisted.internet import defer
from . import builders_config
from . import common
from maxscale import workers
from maxscale.config import constants

DEFAULT_PROPERTIES = {
    "repository": constants.MAXSCALE_REPOSITORY,
    "branch": "develop",
    "target": "develop",
    "maxscale_threads": "8",
    "sysbench_threads": "128"
}


class PerformanceTestSetPropertiesStep(ShellMixin, steps.BuildStep):
    name = 'Set properties'

    def __init__(self, **kwargs):
        kwargs = self.setupShellMixin(kwargs, prohibitArgs=['command'])
        steps.BuildStep.__init__(self, **kwargs)

    @defer.inlineCallbacks
    def run(self):
        # BUILD_TIMESTAMP property
        cmd = yield self.makeRemoteShellCommand(
            command=['date', "+%Y-%m-%d %H-%M-%S"],
            collectStdout=True)
        yield self.runCommand(cmd)
        self.setProperty('BUILD_TIMESTAMP', cmd.stdout[0:-1], 'setProperties')
        # SHELL_SCRIPTS_PATH property
        cmd = yield self.makeRemoteShellCommand(
            command='echo "`pwd`/{}"'.format(builders_config.WORKER_SHELL_SCRIPTS_RELATIVE_PATH),
            collectStdout=True)
        yield self.runCommand(cmd)
        self.setProperty('SHELL_SCRIPTS_PATH', cmd.stdout[0:-1], 'setProperties')
        # WORKSPACE property
        cmd = yield self.makeRemoteShellCommand(
            command='pwd',
            collectStdout=True)
        yield self.runCommand(cmd)
        self.setProperty('WORKSPACE', cmd.stdout[0:-1], 'setProperties')
        # JOB_NAME property
        self.setProperty('JOB_NAME', 'run_test', 'setProperties')
        # custom_builder_id property
        self.setProperty('custom_builder_id', '103', 'setProperties')
        # SYSBENCH_RESULTS_RAW
        self.setProperty('SYSBENCH_RESULTS_RAW', 'Benchmark log parsing finished with an error', 'setProperties')
        # BUILD_ID property
        self.setProperty(
            'BUILD_ID',
            "{}{}".format(self.getProperty('custom_builder_id'),
                          self.getProperty('buildnumber')),
            'setProperties'
        )
        defer.returnValue(0)


def create_factory():
    factory = util.BuildFactory()

    factory.addStep(common.SetDefaultPropertiesStep(default_properties=DEFAULT_PROPERTIES, haltOnFailure=True))

    factory.addStep(PerformanceTestSetPropertiesStep(haltOnFailure=True))

    factory.addStep(steps.Trigger(
        name="Call the 'download_shell_scripts' scheduler",
        schedulerNames=['download_shell_scripts'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=['SHELL_SCRIPTS_PATH']
    ))
    factory.addStep(shell.SetProperty(
        name="Set the 'env' property",
        command="bash -c env",
        haltOnFailure=True,
        extract_fn=common.save_env_to_property,
        env={
            "WORKSPACE": util.Property('WORKSPACE'),
            "JOB_NAME": util.Property('JOB_NAME'),
            "BUILD_ID": util.Property('BUILD_ID'),
            "BUILD_NUMBER": util.Property('BUILD_ID'),
            "BUILD_TIMESTAMP": util.Property('BUILD_TIMESTAMP'),
            "SYSBENCH_RESULTS_RAW": util.Property('SYSBENCH_RESULTS_RAW'),
            "target": util.Property('target'),
            "version": util.Property('version'),
            "maxscale_threads": util.Property('maxscale_threads'),
            "sysbench_threads": util.Property('sysbench_threads')
        }))

    factory.addStep(steps.Git(
        repourl=util.Property('repository'),
        mode='incremental',
        branch=util.Property('branch'),
        haltOnFailure=True))

    # Run performance test and collect
    factory.addStep(steps.ShellCommand(
        name="Run the 'run_performance_test_and_collect.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/run_performance_test_and_collect.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Parse benchmark log
    factory.addStep(steps.ShellCommand(
        name="Run the 'parse_benchmark_log.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/parse_benchmark_log.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Write benchmark results
    factory.addStep(steps.ShellCommand(
        name="Run the 'write_benchmark_results.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/write_benchmark_results.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    return factory


BUILDERS = [
    BuilderConfig(
        name="performance_test",
        workernames=workers.workerNames(),
        factory=create_factory(),
        tags=['test'],
        env=dict(os.environ))
]
