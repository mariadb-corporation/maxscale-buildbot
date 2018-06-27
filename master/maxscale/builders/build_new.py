import os

from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from . import support_new


ENVIRONMENT = {
    "JOB_NAME": util.Property('buildername'),
    "BUILD_ID": util.Property('buildnumber'),
    "BUILD_NUMBER": util.Property('buildnumber'),
    "MDBCI_VM_PATH": util.Property('MDBCI_VM_PATH'),
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


def create_build_factory():
    factory = util.BuildFactory()

    factory.addSteps(support_new.configure_mdbci_vm_path_property())

    factory.addStep(support_new.clone_repository())

    def build_maxscale():
        if not os.path.exists("BUILD/mdbci"):
            os.mkdir("default-maxscale-branch")
            os.chdir("default-maxscale-branch")
            os.system("git clone {}".format(repository))
            os.chdir("..")
        if not os.path.isdir("BUILD"):
            shutil.copytree("default-maxscale-branch/MaxScale/BUILD", ".")
        if not os.path.isdir("BUILD/mdbci"):
            shutil.copytree("default-maxscale-branch/MaxScale/BUILD/mdbci", "BUILD/")
        build_script = "./BUILD/mdbci/build.sh"
        os.execl(build_script, build_script)

    factory.addSteps(support_new.execute_python_script(
        "Build MaxScale using MDBCI", build_maxscale, ["repository"],
        env=ENVIRONMENT))

    factory.addStep(support_new.clean_build_dir())

    factory.addSteps(support_new.clean_build_intermediates())

    return factory


BUILDERS = [
    BuilderConfig(
        name="build_new",
        workernames=["worker1"],
        factory=create_build_factory(),
        tags=['build']
    )
]
