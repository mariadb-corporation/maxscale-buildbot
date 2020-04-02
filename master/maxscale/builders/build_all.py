from buildbot.config import BuilderConfig
from buildbot.plugins import util
from maxscale import workers
from maxscale.builders.support import common
from .build import ENVIRONMENT


def createBuildFactory():
    """
    Creates build factory containing steps
    which triggers build scheduler for each chosen box
    """
    factory = util.BuildFactory()
    factory.addStep(common.BuildAllTrigger(
        name="build_all",
        schedulerNames=['build'],
        waitForFinish=True,
        copy_properties=[
            "branch",
            "build_box_checkbox_container",
            "build_experimental",
            "ci_url",
            "cmake_flags",
            "do_not_destroy_vm",
            "host",
            "old_target",
            "owners",
            "repository",
            "run_upgrade_test",
            "target",
            "try_already_running",
            "version",
        ],
        set_properties={
            "virtual_builder_name": "build"
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_all",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False
    )
]
