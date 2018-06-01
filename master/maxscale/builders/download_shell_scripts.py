import os
from os import listdir
from os.path import isfile, join, basename

from buildbot.plugins import steps, util
from buildbot.config import BuilderConfig


def create_factory():
    factory = util.BuildFactory()

    shell_scripts_files = [join(os.getcwd(), "shell_scripts", f)
                           for f in listdir(join(os.getcwd(), "shell_scripts"))
                           if isfile(join(os.getcwd(), "shell_scripts", f))]
    for file in shell_scripts_files:
        factory.addStep(steps.FileDownload(
            mastersrc=file,
            workerdest=util.Interpolate('%(prop:SHELL_SCRIPTS_PATH)s/{}'.format(basename(file))),
            mode=0o755))

    return factory


BUILDERS = [
    BuilderConfig(
        name="download_shell_scripts",
        workernames=["worker1"],
        factory=create_factory(),
        tags=[],
        env=dict(os.environ))
]
