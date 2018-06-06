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
            "build_full_name": util.Property('build_full_name'),
            "name": util.Property('name'),
            "box": util.Property('box'),
            "try_already_running": util.Property('try_already_running')
        }))
    factory.addStep(steps.ShellCommand(
        name="Run the 'compare_locker_and_build_full_name.sh' script",
        command=[
            'sh',
            util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/compare_locker_and_build_full_name.sh')
        ],
        haltOnFailure=True,
        env=util.Property('env')))
    factory.addStep(steps.Trigger(
        name="Call the 'remove_lock_snapshot' scheduler",
        schedulerNames=['remove_lock_snapshot'], waitForFinish=True,
        alwaysRun=True,
        copy_properties=[
            "name",
        ]))
    # TODO
    # Add doStepIf UNSTABLE_OR_WORSE statement
    factory.addStep(steps.Trigger(
        name="Call the 'smart_remove_lock' scheduler",
        schedulerNames=['smart_remove_lock'],
        waitForFinish=True,
        copy_properties=[
            "build_full_name",
            "box",
            "try_already_running"
        ]))

    return factory


BUILDERS = [
    BuilderConfig(
        name="smart_remove_lock_snapshot",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['axilary'],
        env=dict(os.environ))
]
