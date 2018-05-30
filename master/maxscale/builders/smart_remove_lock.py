import os

from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.steps.trigger import Trigger
from buildbot.steps import shell
from . import common


def create_factory():
    factory = BuildFactory()

    factory.addStep(steps.SetPropertyFromCommand(
        name="Set the 'SHELL_SCRIPTS_PATH' property",
        command='echo "`pwd`/../shell_scripts"',
        property="SHELL_SCRIPTS_PATH",
        haltOnFailure=True, ))
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
            "build_full_name": util.Property('build_full_name'),
            "try_already_running": util.Property('try_already_running'),
            "box": util.Property('box'),
        }))
    factory.addStep(steps.ShellCommand(
        name="Run the 'run_smart_remove_lock_wrapper.sh' script",
        command=['sh', util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/run_smart_remove_lock_wrapper.sh')],
        haltOnFailure=True,
        env=util.Property('env')))
    factory.addStep(Trigger(
        name="Call the 'remove_lock' scheduler",
        schedulerNames=['remove_lock'], waitForFinish=True,
        alwaysRun=True,
        copy_properties=[
            "try_already_running",
            "box",
        ]))

    return factory


BUILDERS = [
    BuilderConfig(
        name="destroy",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['axilary'],
        env=dict(os.environ))
]
