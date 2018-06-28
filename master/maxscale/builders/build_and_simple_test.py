import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.buildstep import ShellMixin
from buildbot.process.factory import BuildFactory
from twisted.internet import defer
from maxscale.change_source.maxscale import get_test_set_by_branch
from maxscale.config import constants
from maxscale import workers
from . import common


DEFAULT_PROPERTIES = {
        "build_experimental": "yes",
        "product": "mariadb",
        "version": constants.DB_VERSIONS[0],
        "do_not_destroy_vm": "no",
        "ci_url": constants.CI_SERVER_URL,
        "backend_ssl": "no",
        "try_already_running": "yes",
        "maxscale_threads": "8",
        "sysbench_threads": "128"
    }


class BuildAndSimpleTestSetPropertiesStep(ShellMixin, steps.BuildStep):
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
        # JOB_NAME property
        self.setProperty('JOB_NAME', 'build_and_simple_test', 'setProperties')
        # custom_builder_id property
        self.setProperty('custom_builder_id', '104', 'setProperties')
        # BUILD_ID property
        self.setProperty(
            'BUILD_ID',
            "{}{}".format(self.getProperty('custom_builder_id'),
                          self.getProperty('buildnumber')),
            'setProperties'
        )
        # target property
        self.setProperty(
            'target',
            "{}-{}".format(self.getProperty('JOB_NAME'),
                           self.getProperty('BUILD_ID')),
            'setProperties'
        )
        # name property
        self.setProperty(
            'name',
            self.getProperty('target'),
            'setProperties'
        )
        # test_set property
        if self.getProperty('test_set') is None:
            self.setProperty(
                'test_set',
                get_test_set_by_branch(self.getProperty('branch')),
                'setProperties'
            )
        # test_branch property
        self.setProperty(
            'test_branch',
            self.getProperty('branch'),
            'setProperties'
        )

        defer.returnValue(0)


def create_factory():
    factory = BuildFactory()

    factory.addStep(common.SetDefaultPropertiesStep(default_properties=DEFAULT_PROPERTIES, haltOnFailure=True))

    factory.addStep(BuildAndSimpleTestSetPropertiesStep(haltOnFailure=True))

    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler. Build Ubuntu",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=[
            "repository",
            "branch",
            "build_experimental",
            "product",
            "version",
            "do_not_destroy_vm",
            "test_set",
            "ci_url"],
        set_properties={
            'box': 'ubuntu_xenial_libvirt',
            'try_already_running': 'yes',
            'target': util.Interpolate("%(prop:target)s-perf"),
            'cmake_flags': '-DBUILD_TESTS=N -DFAKE_CODE=N -DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y',
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'build' scheduler. Build CentOS",
        schedulerNames=['build'],
        waitForFinish=True,
        haltOnFailure=True,
        copy_properties=[
            "repository",
            "branch",
            "build_experimental",
            "product",
            "version",
            "target",
            "do_not_destroy_vm",
            "test_set",
            "ci_url"],
        set_properties={
            'box': 'centos_7_libvirt',
            'try_already_running': 'yes',
            'cmake_flags': ('-DBUILD_TESTS=Y -DCMAKE_BUILD_TYPE=Debug -DFAKE_CODE=Y '
                            '-DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y'),
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'run_test_snapshot' scheduler. Run functional tests",
        schedulerNames=['run_test_snapshot'],
        waitForFinish=True,
        copy_properties=[
            "repository",
            "branch",
            "target",
            "build_experimental",
            "product",
            "version",
            "do_not_destroy_vm",
            "test_set",
            "ci_url",
            "backend_ssl",
            "sysbench_threads",
            "maxscale_threads",
            "try_already_running"],
        set_properties={
            'test_branch': util.Property('branch')
        }
    ))

    factory.addStep(steps.Trigger(
        name="Call the 'performance_test' scheduler. Run performance tests",
        schedulerNames=['performance_test'],
        waitForFinish=True,
        copy_properties=[
            "repository",
            "branch",
            "build_experimental",
            "product",
            "version",
            "do_not_destroy_vm",
            "test_set",
            "ci_url",
            "backend_ssl",
            "sysbench_threads",
            "maxscale_threads",
            "try_already_running"],
        set_properties={
            'target': util.Interpolate("%(prop:target)s-perf")
        }
    ))

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_simple_test",
        workernames=workers.workerNames(),
        factory=create_factory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
