# MaxScale BuildBot

BuildBot configuration for Maxscale

## Using pipenv for installation

In order not to pollute the base system with the BuildBot dependencies it is adviced to use the python virtual environment.

1. Install python3 dependencies: `sudo apt install python3 python3-pip`.
2. Install pipenv to manage virtual environment: `sudo pip3 install pipenv`
3. Go to the `maxscale-buildbot` directory and install dependencies `pipenv install`
4. Enable virtual environment `pipenv shell`.

When done you can leave Python virtual environment by leaving the shell.

If you have installed BuildBot into the virtual environment, then you should either activate environment before running `buildbot` and `buildbot-worker` commands, or use absolute paths to them in the virtual environment directory.

## Buildmaster installation notes

### Database configuration

For production purposes the BuildBot uses the MariaDB database. Use the following template to create the database:

```mysql
create database maxscale_buildbot character set utf8 collate utf8_bin;
grant all privileges on maxscale_buildbot.* to buildbot@localhost identified by '<password>';
```

In order to mitigate the issue of short build step names, the database schema must be updated:
```mysql
ALTER TABLE steps MODIFY name varchar(300);
```

### Application configuration

1. Clone repository or get a repository slice.
2. Install python3 dependencies: `sudo apt install python3 python3-pip`.
3. Install pipenv to manage virtual environment: `sudo pip3 install pipenv`
4. Go to the `maxscale-buildbot` directory and install dependencies `pipenv install`
5. Configure database access in `master/maxscale/config/database_config.py` file. The template for this file can be found in `master/maxscale/config/datababes_config.py` file.
6. Configure mail client in `master/maxscale/config/mailer_config.py` file. The template for this file can be found in `master/maxscale/config/mailer_config_example.py` file.
7. Configure authorization options.
  - When using Google configure credentials in `master/maxscale/config/google_auth_config.py` file. The template for this file can be found in `master/maxscale/config/google_auth_config_example.py` file.
  - When using GitHub configure github client credentials in `master/maxscale/config/github_client_config.py` file. The template for this file can be found in `master/maxscale/config/github_client_config_example.py` file.
8. Configure authorization rights for users in `master/maxscale/config/auth_config.py` file. The template for this file can be found in `master/maxscale/config/auth_config_example.py` file.
9. Configure the list of workers that are allowed to access BuildBot master in `master/maxscale/config/workers.py` file. The template for this file can be found in `master/maxscale/config/workers_example.py` file.
10. Configure the access name of the server in `master/maxscale/conifg/server_config.py` file. The template for this file can be found in `master/maxscale/config/server_config_example.py` file.
11. Create or update BuildBot master configuration: `buildbot upgrade-master master`
12. Start the BuildBot master service: `buildbot start master`.

### GitHub authentication

You must create the OAuth application in GitHub using the [form](https://github.com/settings/applications/new)

The URL of the application must be `BUILDBOT_URL/auth/login`.

The received client identity and secret must be put into `github_client_config.py` file.

## Updating BuildBot master configuration

1. Update the repository configuration.
2. Reload BuildBot configuration: `buildbot reconfig master`.

## Worker installation notes

### Using the manager to install and restart nodes

1. Configure the list of workers for the BuildBot master.
2. Go to the `worker-management` directory and call the `./manage.py --help`.

* If you wish to install workers on the host `first-host` then execute `./manage.py install --host first-host`.
* If you with to restart all workers on all hosts then execute `./manage.py restart`.

### Manual installation

1. Clone the repository or get a repository slice.
2. Install packages that are required to run the worker: `pip3 install -r worker-management/requirements-worker.txt`.
3. Create configuration for the worker: `buildbot-worker create-worker --umask=0o002 DIRECTORY SERVER NAME PASSWORD `, where
   * `DIRECTORY` - path to the worker configuration and build directory.
   * `SERVER` - URI of the server to connect to.
   * `NAME` - name of the worker as specified on the server.
   * `PASSWORD` - password for the specified name.
   * `--umask` - umask for a worker process which determines permission of files created by the worker. The default value for workers is 077. See [Worker Options](http://docs.buildbot.net/current/manual/installation/worker.html#cmdoption-buildbot-worker-create-worker-umask)
4. Fill-in information about the administrator in `DIRECTORY/info/admin` file.
5. Fill-in host description in `DIRECTORY/info/host` file.
6. Start the worker daemon: `bildbot-worker start DIRECTORY`.

# Development notes

## Development environment configuration

In order to efficiently work with the BuildBot codebase you should install development tools:

```
$ pip install -U -r requirements-development.txt
```

## Automated tasks

The common development tasks are automated using the [Paver](https://github.com/paver/paver). There are two common tasks automated:

* `paver check_code` - check Python source code with static code linters.
* `paver check_config` - check BuildBot master configuration.
* `paver buildbot -c start` - run start command for BuildBot in the development mode. You can pass all commands to the BuildBot via this command and `-c` flag.
* `paver restart_buildbot` - restart the BuildBot in the development mode and restart `worker-dev` associated with the environment. You should create the latter one by youself.

## Code standard

The [BuildBot](http://buildbot.net/) project is based on the [Twisted](https://twistedmatrix.com/trac/) framework and uses it's [code standard](https://twistedmatrix.com/documents/current/core/development/policy/coding-standard.html). Therefore the code of BuildBot configuration must follow this coding standard.

## Upgrading the dependencies

The list of Python packages that are required to install the BuildBot master is stored in Pipfile.lock file. In this file the tested and proved to work versions are specified.

In order to migrate to the newer versions you should use Pipenv update command.

```bash
pipenv update
```

When the `Pipfile.lock` file has been updated, the dependencies should be installed.

```shell script
pipenv install
```

1. Activate the virtual environment: `pipenv shell`.
2. Restart the BuildBot master in order to activate installed dependencies: `buildbot restart master`.

The same should be done to the worker requirements file, `requirements-worker.txt`.
