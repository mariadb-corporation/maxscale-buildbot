from buildbot.plugins import schedulers

NIGHTLY_SCHEDULER = schedulers.Nightly(
        name="generate_and_sync_repod",
        builderNames=["generate_and_sync_repod"],
        hour=11, minute=27,
    )

SCHEDULERS = [NIGHTLY_SCHEDULER]
