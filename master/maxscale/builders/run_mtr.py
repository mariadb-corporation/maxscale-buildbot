from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common


ENVIRONMENT = {
    "branch": util.Property('branch'),
    "Image":  util.Property('Image'),
    "mtrParam": util.Property('mtrParam'),
    "target": util.Property('target'),
    "buildID": util.Property('buildID'),
}


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.downloadAndRunScript(
        "mtr/run_mtr.sh",
         name=util.Interpolate(
             "Run MTR target '%(prop:target)s', image '%(prop:Image)s', MTR param '%(prop:mtrParam)s'"
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
        name="run_mtr",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False,
    )
]
