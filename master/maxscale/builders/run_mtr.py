from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common


ENVIRONMENT = {
    "branch": util.Property('branch'),
    "Image":  util.Property('Image'),
    "mtrParam": util.Property('mtrParam'),
    "target": util.Property('target'),
}


def createBuildSteps():
    buildSteps = []
    buildSteps.append(steps.ShellCommand(
        name=util.Interpolate(
            "Run MTR target '%(prop:target)s', image '%(prop:Image)s', MTR param '%(prop:mtrParam)s'"
        ),
        command=["/home/vagrant/es_scritps/run_mtr.sh"]
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
