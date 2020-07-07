from buildbot.plugins import schedulers
from . import properties

BUILD_DOCKER_IMAGE_PROPERTIES = [
    properties.mdbciProductName(),
    properties.build_target(),
    properties.dockerProductName(),
    properties.dockerRegistryURL(),
    properties.host(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_docker_image",
    builderNames=["build_docker_image"],
    buttonName="Build MaxScale Docker image",
    properties=BUILD_DOCKER_IMAGE_PROPERTIES,
    codebases=[properties.maxscaleDockerCodebase()],
)

SCHEDULERS = [MANUAL_SCHEDULER]
