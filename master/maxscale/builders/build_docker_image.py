from buildbot.config import BuilderConfig
from buildbot.plugins import steps, util
from maxscale import workers
from .support import common


def createBuildSteps():
    buildSteps = []
    buildSteps.append(steps.Git(
        repourl=util.Property("maxscale_docker_repository"),
        branch=util.Property("maxscale_docker_repository_branch"),
        mode="full",
    ))
    buildSteps.extend(common.downloadAndRunScript(
        "build_maxscale_docker_image.py",
        args=[
            "--repository", util.Interpolate("%(prop:ci_url)s/%(prop:target)s/mariadb-maxscale/ubuntu"),
            "--tag", util.Property("target"),
            "--name", util.Property("docker_product_name"),
            "--registry", util.Property("docker_registry_url")
        ],
        workdir=util.Interpolate("%(prop:builddir)s/build/maxscale/"),
    ))
    return buildSteps


def createBuildfactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_docker_image",
        workernames=workers.workerNames(),
        factory=createBuildfactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["BUILD"],
        collapseRequests=False
    )
]
