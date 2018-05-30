from buildbot.plugins import schedulers


TRIGGERABLE_SCHEDULER = schedulers.Triggerable(
    name="download_shell_scripts",
    builderNames=["download_shell_scripts"]
)

SCHEDULERS = [TRIGGERABLE_SCHEDULER]
