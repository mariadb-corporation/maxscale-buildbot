from buildbot.plugins import schedulers
from . import properties

BUILD_DOCKER_IMAGE_PROPERTIES = [
    properties.build_target(),
    properties.ci_url(),
    properties.dockerProductName(),
    properties.dockerRegistryURL(),
    properties.maxscaleDockerRepository(),
    properties.maxscaleDockerRepositoryBranch(),
    properties.host(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_docker_image",
    builderNames=["build_docker_image"],
    buttonName="Build MaxScale Docker image",
    properties=BUILD_DOCKER_IMAGE_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
