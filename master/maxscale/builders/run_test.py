import os

from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from buildbot.process.buildstep import BuildStep
from buildbot.process.buildstep import ShellMixin
from buildbot.process.factory import BuildFactory
from buildbot.steps.trigger import Trigger
from buildbot.steps import shell
from twisted.internet import defer
from maxscale.config import constants
from . import common


class RunTestSetPropertiesStep(ShellMixin, BuildStep):
    name = 'Set properties'

    def __init__(self, **kwargs):
        kwargs = self.setupShellMixin(kwargs, prohibitArgs=['command'])
        BuildStep.__init__(self, **kwargs)

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
                            command='echo "`pwd`/{}"'.format(constants.WORKER_SHELL_SCRIPTS_RELATIVE_PATH),
                            collectStdout=True)
        yield self.runCommand(cmd)
        self.setProperty('SHELL_SCRIPTS_PATH', cmd.stdout[0:-1], 'setProperties')
        # WORKSPACE property
        cmd = yield self.makeRemoteShellCommand(
                            command='echo "`pwd`/{}"'.format(constants.WORKER_WORKSPACE_RELATIVE_PATH),
                            collectStdout=True)
        yield self.runCommand(cmd)
        self.setProperty('WORKSPACE', cmd.stdout[0:-1], 'setProperties')
        # JOB_NAME property
        self.setProperty('JOB_NAME', 'run_test', 'setProperties')
        # custom_builder_id property
        self.setProperty('custom_builder_id', '101', 'setProperties')
        # BUILD_ID property
        self.setProperty('BUILD_ID', "{}{}".format(self.getProperty('custom_builder_id'),
                                                   self.getProperty('buildnumber')), 'setProperties')
        defer.returnValue(0)


def create_factory():
    factory = BuildFactory()

    factory.addStep(RunTestSetPropertiesStep(haltOnFailure=True))
    factory.addStep(Trigger(
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
            "BUILD_LOG_PARSING_RESULT": 'Build log parsing finished with an error',
            "name": util.Property('name'),
            "target": util.Property('target'),
            "box": util.Property('box'),
            "product": util.Property('product'),
            "version": util.Property('version'),
            "do_not_destroy_vm": util.Property('do_not_destroy_vm'),
            "test_set": util.Property('test_set'),
            "ci_url": util.Property('ci_url'),
            "smoke": util.Property('smoke'),
            "big": util.Property('big'),
            "backend_ssl": util.Property('backend_ssl'),
            "use_snapshots": util.Property('use_snapshots'),
            "logs_dir": util.Property('logs_dir'),
            "no_vm_revert": util.Property('no_vm_revert'),
            "template": util.Property('template'),
            "config_to_clone": util.Property('config_to_clone'),
            "test_branch": util.Property('branch'),
        }))

    # Create workspace
    factory.addStep(steps.ShellCommand(
        name="Create workspace directory",
        command=common.create_workspace_command,
        alwaysRun=True,
        env=util.Property('env')))

    factory.addStep(steps.Git(
        repourl=util.Property('repository'),
        mode='incremental',
        branch=util.Property('branch'),
        haltOnFailure=True))

    # Run test and collect
    factory.addStep(steps.ShellCommand(
        name="Run the 'run_test_and_collect.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/run_test_and_collect.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Parse build log
    factory.addStep(steps.ShellCommand(
        name="Run the 'parse_build_log.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/parse_build_log.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Create env coredumps
    factory.addStep(steps.ShellCommand(
        name="Run the 'create_env_coredumps.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/create_env_coredumps.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Write build results
    factory.addStep(steps.ShellCommand(
        name="Run the 'write_build_results.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/write_build_results.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Publish report portal
    factory.addStep(steps.ShellCommand(
        name="Run the 'publish_report_portal.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/publish_report_portal.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    # Save the '$WORKSPACE/results_$BUILD_ID' content to the 'build_results_content' property
    factory.addStep(shell.SetProperty(
        name="Save the '$WORKSPACE/results_$BUILD_ID' content to the 'build_results_content' property",
        property="build_results_content",
        command=util.Interpolate("cat %(prop:WORKSPACE)s/results_%(prop:BUILD_ID)s"),
        haltOnFailure=True, ))

    # Save the '$WORKSPACE/coredumps_$BUILD_ID' content to the 'coredumps_results_content' property
    factory.addStep(shell.SetProperty(
        name="Save the '$WORKSPACE/coredumps_$BUILD_ID' content to the 'coredumps_results_content' property",
        property="coredumps_results_content",
        command=util.Interpolate("cat %(prop:WORKSPACE)s/coredumps_%(prop:BUILD_ID)s"),
        haltOnFailure=True, ))

    # Workspace cleanup
    factory.addStep(steps.ShellCommand(
        name="Workspace cleanup",
        command=common.clean_workspace_command,
        alwaysRun=True,
        env=util.Property('env')))

    factory.addStep(Trigger(
        name="Call the 'cleanup' scheduler",
        schedulerNames=['cleanup'],
        waitForFinish=True,
        alwaysRun=True,
        copy_properties=[
            "name",
            "do_not_destroy_vm",
            "box",
        ],
        set_properties={
            "build_full_name": util.Interpolate('%(prop:JOB_NAME)s-%(prop:BUILD_ID)s')}
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="run_test",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['test'],
        env=dict(os.environ))
]
