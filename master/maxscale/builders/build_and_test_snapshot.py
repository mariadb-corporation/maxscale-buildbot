import os

from buildbot.plugins import util, steps
from buildbot.config import BuilderConfig
from buildbot.process.factory import BuildFactory
from maxscale import workers


def createFactory():
    factory = BuildFactory()
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
            "ci_url"],
        set_properties={
            'box': 'ubuntu_xenial_libvirt',
            'try_already_running': 'yes',
            'target': util.Interpolate("%(prop:target)s-perf"),
            'cmake_flags': '-DBUILD_TESTS=Y -DCMAKE_BUILD_TYPE=Debug -DFAKE_CODE=Y-DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y',
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
            "test_set",
            "ci_url",
            "backend_ssl"],
        set_properties={
            "box": "centos_7_libvirt",
            "test_branch": util.Property("branch")
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_and_test_snapshot",
        workernames=workers.workerNames(),
        factory=createFactory(),
        tags=['build', 'test'],
        env=dict(os.environ))
]
