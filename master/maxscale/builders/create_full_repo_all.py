from buildbot.config import BuilderConfig
from buildbot.plugins import util
from maxscale import workers
from maxscale.builders.support import common
from .build import ENVIRONMENT


def createCreateFullRepoFactory():
    """
    Creates create factory containing steps
    which triggers create_full_repo scheduler for each chosen box
    """
    factory = util.BuildFactory()
    factory.addStep(common.BuildAllTrigger(
        name="create_full_repo_all",
        schedulerNames=['create_full_repo'],
        waitForFinish=True,
        copy_properties=[
            "branch",
            "host",
            "owners",
            "repository",
            "version",
            "target",
            "do_not_destroy_vm",
            "ci_url",
            "major_ver",
            "build_box_checkbox_container"
        ],
        set_properties={
            "virtual_builder_name": "create_full_repo"
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="create_full_repo_all",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=createCreateFullRepoFactory(),
        tags=["create_full_repo"],
        env=ENVIRONMENT,
        collapseRequests=False
    )
]
