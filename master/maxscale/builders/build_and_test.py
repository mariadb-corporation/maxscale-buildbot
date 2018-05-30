import os

from buildbot.plugins import util
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from buildbot.steps.trigger import Trigger


def create_factory():
    factory = BuildFactory()

    factory.addStep(Trigger(
        name="Call the 'build' scheduler",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=[
            "name",
            "repository",
            "branch",
            "target",
            "build_experimental",
            "box",
            "product",
            "version",
            "cmake_flags"
            "do_not_destroy_vm",
            "test_set",
            "ci_url",
            "smoke",
            "big"]
    ))

    factory.addStep(Trigger(
        name="Call the 'run_test' scheduler",
        schedulerNames=['run_test'],
        waitForFinish=True,
        copy_properties=[
            "name",
            "repository",
            "branch",
            "target",
            "build_experimental",
            "box",
            "product",
            "version",
            "cmake_flags"
            "do_not_destroy_vm",
            "test_set",
            "ci_url",
            "smoke",
            "big"],
        set_properties={'test_branch': util.Property('branch')}
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test",
        workernames=["worker1"],
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
