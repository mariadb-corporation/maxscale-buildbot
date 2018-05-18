# maxscale-buildbot

BuildBot configuration for Maxscale

## Using virtualenv for installation

In order not to pollute the base system with the BuildBot dependencies it is adviced to use the python virtual environment.

1. Install python3 virtual environment: `sudo apt install python3-virtualenv`.
2. Create virtual environment: `python3 -m virtualenv -p /usr/bin/python3 v-env`.
3. Enable virtual environment for current bash process: `source v-env/bin/activate`.

When done you can deactivate Python virtual environment running `deactivate` command.

If you have installed BuildBot into the virtual environment, then you should either activate environment before running `buildbot` and `buildbot-worker` commands, or use absolute paths to them in the virtual environment directory.

## Buildmaster installation notes

1. Clone repository or get a repository slice.
2. Install packages that are reqired to build Python dependencies: `sudo apt install -y build-essential python3-dev`
2. Install all Python dependencies that are needed by the buildmaster: `pip3 install -r requirements.txt`.
3. Create or update buildmaster configuration: `buildbot upgrade-master buildbot-master/master`
4. Start the buildmaster service: `buildbot start buildbot-master/master`

## Updating Buildmaster configuration

1. Update the repository configuration.
2. Reload buildbot configuration: `buildbot reconfig buildbot-master/master`
