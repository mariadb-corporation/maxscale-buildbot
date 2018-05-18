# maxscale-buildbot

BuildBot configuration for Maxscale

## Buildmaster installation notes

1. Clone repository or get a repository slice.
2. Install all dependencies that are needed by the buildmaster: `pip3 install -r requirements.txt`.
3. Create or update buildmaster configuration: `buildbot upgrade-master buildbot-master/master`
4. Start the buildmaster service: `buildbot start buildbot-master/master`

## Updating Buildmaster configuration

1. Update the repository configuration.
2. Reload buildbot configuration: `buildbot reconfig buildbot-master/master`
