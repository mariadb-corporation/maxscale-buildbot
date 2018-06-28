import os

from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig
from buildbot.steps import shell
from maxscale import workers
from . import common


def create_factory():
    factory = util.BuildFactory()
    factory.addStep(shell.SetProperty(
        name="Set the 'env' property",
        command="bash -c env",
        haltOnFailure=True,
        extract_fn=common.save_env_to_property,
        env={
            "name": util.Property('name'),
        }))
    factory.addStep(steps.ShellCommand(command="rm $MDBCI_VM_PATH/${name}_snapshot_lock", env=util.Property('env')))

    return factory


BUILDERS = [
    BuilderConfig(
        name="remove_lock_snapshot",
        workernames=workers.workerNames(),
        factory=create_factory(),
        tags=['axilary'],
        env=dict(os.environ))
]
