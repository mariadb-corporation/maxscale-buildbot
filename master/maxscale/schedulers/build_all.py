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

NIGHTLY_22_SCHEDULER = schedulers.Nightly(
    name='nightly_22',
    branch='2.2',
    builderNames=['build_all'],
    hour=14, minute=6,
    codebases={
        'codebase1': {
            'branch': '2.2',
            'repository': constants.MAXSCALE_REPOSITORY
        }
    },
    properties=properties.extractDefaultValues(BUILD_ALL_PROPERTIES)
)

SCHEDULERS = [MANUAL_SCHEDULER, NIGHTLY_22_SCHEDULER]
