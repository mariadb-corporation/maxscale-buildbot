import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from buildbot.process.buildstep import ShellMixin
from twisted.internet import defer
from . import builders_config
from . import common


class BuildSetPropertiesStep(ShellMixin, steps.BuildStep):
    name = 'Set properties'

    def __init__(self, **kwargs):
        kwargs = self.setupShellMixin(kwargs, prohibitArgs=['command'])
        steps.BuildStep.__init__(self, **kwargs)

    @defer.inlineCallbacks
    def run(self):
        # SHELL_SCRIPTS_PATH property
        cmd = yield self.makeRemoteShellCommand(
            command='echo "`pwd`/{}"'.format(builders_config.WORKER_SHELL_SCRIPTS_RELATIVE_PATH),
            collectStdout=True)
        yield self.runCommand(cmd)
        self.setProperty('SHELL_SCRIPTS_PATH', cmd.stdout[0:-1], 'setProperties')
        # JOB_NAME property
        self.setProperty('JOB_NAME', 'build', 'setProperties')
        # custom_builder_id property
        self.setProperty('custom_builder_id', '100', 'setProperties')
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

    factory.addStep(BuildSetPropertiesStep(haltOnFailure=True))

    factory.addStep(steps.Trigger(
        name="Call the 'download_shell_scripts' scheduler",
        schedulerNames=['download_shell_scripts'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=['SHELL_SCRIPTS_PATH']
    ))

    factory.addStep(steps.Git(
        repourl=util.Property('repository'),
        branch=util.Property('branch'),
        mode='incremental',
        haltOnFailure=True))

    factory.addStep(steps.ShellCommand(
        name="Run the 'run_build.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/run_build.sh')],
        haltOnFailure=True))

    # Workspace cleanup
    factory.addStep(steps.ShellCommand(
        name="Workspace cleanup",
        command=common.clean_workspace_command,
        alwaysRun=True))

    factory.addStep(steps.Trigger(
        name="Call the 'cleanup' scheduler",
        schedulerNames=['cleanup'],
        waitForFinish=True,
        alwaysRun=True,
        copy_properties=[
            "do_not_destroy_vm",
            "try_already_running",
            "box",
        ],
        set_properties={
            "build_full_name": util.Interpolate('%(prop:JOB_NAME)s-%(prop:BUILD_ID)s'),
            "name": util.Interpolate('%(prop:box)s-%(prop:JOB_NAME)s-%(prop:BUILD_ID)s')}
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['build'],
        env={
            "WORKSPACE": util.Property('builddir'),
            "JOB_NAME": util.Property('JOB_NAME'),
            "BUILD_ID": util.Property('BUILD_ID'),
            "BUILD_NUMBER": util.Property('BUILD_ID'),
            "box": util.Property('box'),
            "target": util.Property('target'),
            "cmake_flags": util.Property('cmake_flags'),
            "do_not_destroy_vm": util.Property('do_not_destroy_vm'),
            "build_experimental": util.Property('build_experimental'),
            "try_already_running": util.Property('try_already_running'),
            "run_upgrade_test": util.Property('run_upgrade_test'),
            "old_target": util.Property('old_target'),
            "ci_url": util.Property('ci_url')
        }
    )
]
