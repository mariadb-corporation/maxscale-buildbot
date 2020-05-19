from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common


def buildMdbci():
    """This script will be run on the worker"""
    return steps.ShellCommand(
        name="Build MDBCI",
        command=["./package/build.sh", util.Property("buildnumber")]
    )


def publishMdbci():
    return steps.ShellCommand(
        name="Copy MDBCI AppImage to CI repository",
        command=util.Interpolate(
            """
            mdbci_file=`ls %(prop:builddir)s/build/package/build/result/* | xargs -n1 basename`;
            scp %(prop:builddir)s/build/package/build/result/${mdbci_file} %(prop:upload_server)s:/srv/repository/MDBCI/;
            ssh %(prop:upload_server)s chmod 755 /srv/repository/MDBCI/${mdbci_file};
            ssh %(prop:upload_server)s unlink /srv/repository/MDBCI/mdbci;
            ssh %(prop:upload_server)s ln -s /srv/repository/MDBCI/${mdbci_file} /srv/repository/MDBCI/mdbci
            """),
        alwaysRun=False)

def configureBuildProperties(properties):
    return {
        "upload_server" : constants.UPLOAD_SERVERS[properties.getProperty("host")],
    }

def createBuildFactory():
    factory = util.BuildFactory()
    factory.addStep(steps.SetProperties(properties=configureCommonProperties))
    factory.addSteps(common.cloneRepository())
    factory.addStep(buildMdbci())
    factory.addStep(publishMdbci())
    factory.addSteps(common.cleanBuildDir())
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_mdbci",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        tags=["build_mdbci"],
        collapseRequests=False,
    )
]
