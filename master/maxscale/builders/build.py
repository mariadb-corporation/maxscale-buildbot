import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from . import support


ENVIRONMENT = {
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


@util.renderer
def configure_build_properties(properties):
    custom_builder_id = "100"
    build_id = util.Interpolate("%(kw:builder_id)s%(prop:buildnumber)s",
                                builder_id=custom_builder_id)
    job_name = 'build'
    return {
        "JOB_NAME": job_name,
        "custom_builder_id": custom_builder_id,
        "BULDR_ID": build_id,
        "build_full_name": util.Interpolate('%(kw:job_name)s-%(kw:build_id)s',
                                            job_name=job_name, build_id=build_id),
        "name": util.Interpolate('%(prop:box)s-%(kw:job_name)s-%(kw:build_id)s',
                                 job_name=job_name, build_id=build_id),
        "MDBCI_VM_PATH": util.Interpolate("%(prop:HOME)s/vms")
    }


def create_build_factory():
    factory = util.BuildFactory()

    factory.addStep(support.get_worker_home_directory())

    factory.addStep(steps.SetProperties(properties=configure_build_properties))

    factory.addStep(support.clone_repository())

    factory.addSteps(support.execute_shell_script('run_build.sh'))

    factory.addStep(support.clean_build_dir())

    factory.addSteps(support.clean_build_intermediates())

    return factory


BUILDERS = [
    BuilderConfig(
        name="build",
        workernames=workers.workerNames(),
        factory=create_build_factory(),
        tags=['build'],
        env=ENVIRONMENT
    )
]
