from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common

ENVIRONMENT = {
    "target": util.Property('target'),
    "branch": util.Property('branch'),
}


def createBuildSteps():
    buildSteps = []
    buildSteps.extend(common.cloneRepository(util.Secret("mdbeSshIdentity")))
    buildSteps.extend(common.downloadAndRunScript(
        "mtr/build_source_tar.sh",
         name=util.Interpolate(
             "Build source tarball branch '%(prop:branch)s', target '%(prop:target)s'"
         ),
        workdir=util.Interpolate("%(prop:builddir)s"),
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
        name="build_es_star",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False,
    )
]
