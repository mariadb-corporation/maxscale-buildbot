import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.steps import shell
from . import common


def create_factory():
    factory = BuildFactory()

    factory.addStep(shell.SetProperty(
        name="Set the 'env' property",
        command="bash -c env",
        haltOnFailure=True,
        extract_fn=common.save_env_to_property,
        env={
            "name": util.Property('name'),
            "do_not_destroy_vm": util.Property('do_not_destroy_vm'),
            "build_full_name": util.Property('build_full_name'),
            "try_already_running": util.Property('try_already_running'),
            "box": util.Property('box'),
        }))
    factory.addStep(steps.Trigger(
        name="Call the 'destroy' scheduler",
        schedulerNames=['destroy'],
        waitForFinish=True,
        copy_properties=[
            "name",
            "do_not_destroy_vm",
            "try_already_running",
        ]))
    factory.addStep(steps.Trigger(
        name="Call the 'smart_remove_lock' scheduler",
        schedulerNames=['smart_remove_lock'],
        waitForFinish=True,
        copy_properties=[
            "build_full_name",
            "try_already_running",
            "box",
        ]))

    return factory


BUILDERS = [
    BuilderConfig(
        name="cleanup",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['cleanup'],
        env=dict(os.environ))
]
