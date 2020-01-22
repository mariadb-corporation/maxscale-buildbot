from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common

ENVIRONMENT = {
    "branch": util.Property('branch'),
    "target": util.Property('target'),
    "Image":  util.Property('Image'),
    "BuildType": util.Property('BuildType'),
    "buildID": util.Property('buildID'),
}


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.downloadAndRunScript(
        "mtr/build_es.sh",
        name=util.Interpolate(
            "Build binary target '%(prop:target)s', image '%(prop:Image)s', build type '%(prop:BuildType)s'"
        ),
    ))
    buildSteps.extend(common.removeRootFiles())
    buildSteps.extend(common.cleanBuildDir())
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_es_bin",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False,
    )
]
