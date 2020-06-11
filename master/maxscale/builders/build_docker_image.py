from buildbot.config import BuilderConfig
from buildbot.plugins import steps, util
from maxscale import workers
from maxscale.config import constants
from .support import common


def createBuildfactory():
    factory = util.BuildFactory()
    factory.addSteps(common.cloneRepository())
    factory.addStep(steps.ShellCommand(
        name=util.Interpolate("Register in the Docker Registry %(prop:docker_registry_url)s"),
        command=["docker", "login", util.Property("docker_registry_url"),
                 "--username", constants.DOCKER_REGISTRY_USER_NAME,
                 "--password", util.Secret("dockerRegistryPassword")
                 ],
        haltOnFailure=True
    ))
    factory.addSteps(common.downloadAndRunScript(
        name=util.Interpolate("Build docker image for %(prop:target)s"),
        scriptName="build_maxscale_docker_image.py",
        args=[
            "--repository", util.Interpolate("%(prop:ci_url)s/%(prop:target)s/mariadb-maxscale/ubuntu"),
            "--tag", util.Property("target"),
            "--name", util.Property("docker_product_name"),
            "--registry", util.Property("docker_registry_url")
        ],
        workdir=util.Interpolate("%(prop:builddir)s/build/maxscale/"),
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_docker_image",
        workernames=workers.workerNames(),
        factory=createBuildfactory(),
        nextWorker=common.assignWorker,
        tags=["BUILD"],
        collapseRequests=False
    )
]
