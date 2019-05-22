from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

PUBLISH_RELEASE_PROPERTIES = [
    properties.version_number(),
    properties.host(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="publish_release",
    builderNames=["publish_release"],
    buttonName="Publish Release",
    codebases=properties.codebaseParameter(),
    properties=PUBLISH_RELEASE_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
