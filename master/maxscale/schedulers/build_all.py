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
    codebases=[
        common.maxscale_codebase()
    ],
    properties=BUILD_ALL_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]

for branch in constants.NIGHTLY_SCHEDS:
    NIGHTLY_PROPERTIES = properties.extractDefaultValues(BUILD_ALL_PROPERTIES)
    del NIGHTLY_PROPERTIES['target']
    NIGHTLY_PROPERTIES['target'] = branch

    NIGHTLY_SCHEDULER = schedulers.Nightly(
        name=branch,
        builderNames=['build_all'],
        hour=4, minute=0,
        codebases={
            'codebase1': {
                'branch': branch,
                'repository': constants.MAXSCALE_REPOSITORY
            }
        },
        properties=NIGHTLY_PROPERTIES
        )
    SCHEDULERS.append(NIGHTLY_SCHEDULER)
    continue

