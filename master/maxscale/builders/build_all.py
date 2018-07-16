from buildbot.config import BuilderConfig
from buildbot.plugins import util
from maxscale import workers
from maxscale.builders.support.support import BuildAllTrigger
from .build import ENVIRONMENT


def createBuildFactory():
    """
    Creates build factory containing steps
    which triggers build scheduler for each chosen box
    """
    factory = util.BuildFactory()
    factory.addStep(BuildAllTrigger(
        name="build_all",
        schedulerNames=['build_all'],
        waitForFinish=True,
        copy_properties=[
            "name",
            "repository",
            "branch",
            "build_box_checkbox_container",
            "target",
            "build_experimental",
            "product",
            "version",
            "cmake_flags"
            "do_not_destroy_vm",
            "try_already_running",
            "test_set",
            "ci_url",
            "smoke",
            "big"],
        set_properties={
            "virtual_builder_name": "build"
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_all",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT
    )
]
