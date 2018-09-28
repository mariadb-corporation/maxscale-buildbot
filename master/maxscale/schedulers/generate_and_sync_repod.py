from buildbot.plugins import schedulers

NIGHTLY_SCHEDULER = schedulers.Nightly(
        name="generate_and_sync_repod",
        builderNames=["generate_and_sync_repod"],
        hour=9, minute=00,
    )

SCHEDULERS = [NIGHTLY_SCHEDULER]
