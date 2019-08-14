from buildbot.plugins import schedulers
from maxscale.schedulers.create_full_repo import BUILD_PROPERTIES
from . import properties

BUILD_PROPERTIES = [properties.buildBoxCheckboxContainer()] + BUILD_PROPERTIES[1:]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="create_full_repo_all",
    builderNames=["create_full_repo_all"],
    buttonName="Create full repo all",
    codebases=properties.codebaseParameter(),
    properties=BUILD_PROPERTIES
)

TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="create_full_repo_all_triggerable",
    builderNames=["create_full_repo_all"],
    properties=properties.extractDefaultValues([properties.buildBoxCheckboxContainer()])
)

SCHEDULERS = [MANUAL_SCHEDULER, TRIGGERABLE_SCHEDULER]
