import os

from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from buildbot.steps import shell
from . import common


def create_factory():
    factory = util.BuildFactory()

    factory.addStep(steps.SetPropertyFromCommand(
        name="Set the 'SHELL_SCRIPTS_PATH' property",
        command='echo "`pwd`/../shell_scripts"',
        property="SHELL_SCRIPTS_PATH",
        haltOnFailure=True, ))
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
            "try_already_running": util.Property('try_already_running'),
            "box": util.Property('box'),
        }))
    factory.addStep(steps.ShellCommand(
        name="Run the 'run_remove_lock.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/run_remove_lock.sh')],
        haltOnFailure=True,
        env=util.Property('env')))

    return factory


BUILDERS = [
    BuilderConfig(
        name="remove_lock",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['axilary'],
        env=dict(os.environ))
]
