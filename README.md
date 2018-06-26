# Maxscale BuildBot

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
3. Create or update buildmaster configuration: `buildbot upgrade-master master`
4. Configure mail client in `master/maxscale/config/mailer_config.py` file. The template for this file can be found in `master/maxscale/config/mailer_config_example.py` file.
5. Configure github client in `master/maxscale/config/github_client_config.py` file. The template for this file can be found in `master/maxscale/config/github_client_config_example.py` file.
6. Configure authorization rights for users in `master/maxscale/config/auth_config.py` file. The template for this file can be found in `master/maxscale/config/auth_config_example.py` file.
7. Start the buildmaster service: `buildbot start master`

## Updating Buildmaster configuration

1. Update the repository configuration.
2. Reload buildbot configuration: `buildbot reconfig master`

# Development notes

The common development tasks are automated using the [Paver](https://github.com/paver/paver). There are two common tasks automated:

* `paver check_code` - check Python source code with static code linters.
* `paver check_config` - check BuildBot master configuration.
* `paver buildbot -c start` - run start command for buildbot in the development mode. You can pass all commands to the buildbot via this command and `-c` flag.
* `paver restart_buildbot` - restart the buildbot in the development mode and restart `worker-dev` associated with the environment. You should create the latter one by youself.

## Upgrading the dependencies

The list of Python packages that are required to install the BuildBot master is stored in [`requirements.txt`](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/requirements.txt) file. In this file the tested and proved to work versions are specified.

In orded to migrate to the newer versions you should either specify them directly in the file or use the [pur](https://pypi.org/project/pur/) utility. The latter one upgrades all dependencise to the latest version available. Be adviced, that it might not be the right approach. In order to use `pur`, launch it the following way:

```bash
$ pyr -r requirements.txt
```

When the `requirements.txt` file has been updated, the dependencies should be installed in the Python virtual environment.

1. Activate the virtual environment: `source v-env/bin/activate`.
2. Upgrade dependencies: `pip install -U -r requirements.txt`.
3. Restart the BuildBot master in order to activate installed dependecsies: `buildbot restart master`.
