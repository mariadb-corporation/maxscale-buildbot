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
            cp %(prop:builddir)s/build/package/build/result/${mdbci_file} $HOME/%(prop:repo_path)s/;
            chmod 755 $HOME/%(prop:repo_path)s/${mdbci_file};
            unlink $HOME/%(prop:repo_path)s/mdbci;
            ln -s $HOME/%(prop:repo_path)s/${mdbci_file} $HOME/%(prop:repo_path)s/mdbci
            """),
        alwaysRun=False)


def createBuildFactory():
    factory = util.BuildFactory()
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
