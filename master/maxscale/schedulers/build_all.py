from buildbot.plugins import schedulers
from maxscale.schedulers.build import BUILD_PROPERTIES
from maxscale.config import constants
from . import properties
from . import common

BUILD_ALL_PROPERTIES = [properties.buildBoxCheckboxContainer()] + BUILD_PROPERTIES[1:]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_all",
    builderNames=["build_all"],
    buttonName="Build all",
    codebases=properties.codebaseParameter(),
    properties=BUILD_ALL_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]

# Add schedulers for every active branch to be built every night
# The list of branches is defined by constants.NIGHTLY_SCHEDS
# (see maxscale/config/constants.py)
for branch in constants.NIGHTLY_SCHEDS:
    nightlyProperties = properties.extractDefaultValues(BUILD_ALL_PROPERTIES)
    nightlyProperties['target'] = branch

    nightlyScheduler = schedulers.Nightly(
        name=branch,
        builderNames=['build_all'],
        hour=4, minute=0,
        codebases={"": {
            "branch": branch,
            "repository": constants.MAXSCALE_REPOSITORY
        }},
        properties=nightlyProperties
    )
    SCHEDULERS.append(nightlyScheduler)
