from buildbot.plugins import schedulers
from maxscale.schedulers.build import BUILD_PROPERTIES
from . import properties
from . import common


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_all",
    builderNames=["build_all"],
    buttonName="Build all",
    codebases=[
        common.maxscale_codebase()
    ],
    properties=[properties.buildBoxCheckboxContainer()] + BUILD_PROPERTIES[1:]
)

SCHEDULERS = [MANUAL_SCHEDULER]
