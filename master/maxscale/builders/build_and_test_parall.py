import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers
from maxscale.builders.support import common

COMMON_PROPERTIES = {
    "big": util.Property("big"),
    "box": util.Property("box"),
    "branch": util.Property("branch"),
    "build_experimental": util.Property("build_experimental"),
    "ci_url": util.Property("ci_url"),
    "cmake_flags": util.Property("cmake_flags"),
    "do_not_destroy_vm": util.Property("do_not_destroy_vm"),
    "host": util.Property("host"),
    "owners": util.Property("owners"),
    "product": util.Property("product"),
    "repository": util.Property("repository"),
    "smoke": util.Property("smoke"),
    "target": util.Property("target"),
    "version": util.Property("version"),
}


class ParallelRunTestTrigger(steps.Trigger):
    """
    Special trigger that allows to spawn a run_test task with "test_set" and "name"
    arguments specified for each of the triggered task.
    """
    def __init__(self, testSetAmount=1, **kwargs):
        self.testSetAmount = testSetAmount
        super().__init__(**kwargs)

    def getSchedulersAndProperties(self):
        schedulers = []
        for testSet in range(1, self.testSetAmount + 1):
            propertiesToSet = self.set_properties.copy()
            propertiesToSet.update({
                "test_set": '-L set{:02d}'.format(testSet),
                "name": ('{}-{:02d}'.format(self.getProperty("name"), testSet)),
            })
            for schedulerName in self.schedulerNames:
                schedulers.append({
                    "sched_name": schedulerName,
                    "props_to_set": propertiesToSet,
                    "unimportant": schedulerName in self.unimportantSchedulerNames
                })
        return schedulers


def create_factory():
    factory = BuildFactory()
    factory.addSteps(common.initTargetProperty())
    factory.addSteps(common.initNameProperty())
    buildProperties = COMMON_PROPERTIES.copy()
    buildProperties.update({
        'virtual_builder_name': util.Interpolate('Build for %(prop:box)s'),
    })
    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=False,
        set_properties=buildProperties,
    ))
    runTestProperties = COMMON_PROPERTIES.copy()
    runTestProperties.update({
        "backend_ssl": util.Property("backend_ssl"),
        "test_branch": util.Property('branch'),
        "use_callgrind": util.Property("use_callgrind"),
        "use_valgrind": util.Property("use_valgrind"),
    })
    factory.addStep(ParallelRunTestTrigger(
        name="Call the 'run_test' for each test set",
        testSetAmount=3,
        schedulerNames=['run_test'],
        waitForFinish=True,
        set_properties=runTestProperties,
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_parall",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
