from buildbot.plugins import schedulers

NIGHTLY_SCHEDULER = schedulers.Nightly(
        name="generate_and_sync_repod",
        builderNames=["generate_and_sync_repod"],
        hour=9, minute=00,
    )

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="generate_and_sync_repod_manually",
    buttonName="Start generation",
    builderNames=["generate_and_sync_repod"]
)

SCHEDULERS = [NIGHTLY_SCHEDULER, MANUAL_SCHEDULER]
