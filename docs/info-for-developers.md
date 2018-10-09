# Information for developers

## Architecture

The main configuration file is [master/master.cfg](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/master.cfg). It initializes the `BuildmasterConfig` object. This object is a dict in which all components of the project are written (builders, schedulers, etc.).

All components are located in the directory [master/maxscale](https://github.com/mariadb-corporation/maxscale-buildbot/tree/master/master/maxscale) in their respective directories.

List of components:
* Builders
* Schedulers
* Change source
* Auth
* Services (MailNotifiers)

## Builders

The builders are in the [master/maxscale/builders](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders). Builders describe the steps of the task.

### Default properties
In some builders, dicts `DEFAULT_PROPERTIES` with the default values are declared for the builder properties (for example, [Build builder](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py)). `DEFAULT_PROPERTIES` is used if any property of the builder at launch is not specified. For specify default properties, builder use [master/maxscale/builders/common.SetDefaultPropertiesStep](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/common.py), which sets the missing properties to the default value.

### Environmental variables on the remote worker
Each worker has its separate environment. To create environmental variable on worker a dictionary with variable's name and value must be created and passed to `env` property of the builder's configuration.
[Dictionary with environmental variables](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py#L8) can use render build's properties as variable's value to pass properties to worker's environment.
Alternatively master's environment can be copied to worker by assigning `dict(os.environ))` to the `env` argument of builder's configureation.

### Custom Build Step
In some builders, to specify a group of properties in one step, you can use your own class, inherited from `steps.BuildStep` ([Custom Buildsteps docs](http://docs.buildbot.net/current/manual/customization.html#writing-new-buildsteps)). For example,  [Build builder](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py) use own BuildSetPropertiesStep class for it.

### Remote Python scripts
Python functions can be executed on a worker using [maxscale.builders.support.support.executePythonScript(name, function, modules=(), **kwargs)](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/support.py#L50) function. This functions will transform Python function into a string and transfer it to `<builddir>/build/script` directory on the remote worker.
All build's properties are imported to the script as a local variables. Following modules are imported by default: sys, os, os.path, shutil, subprocess and additional modules can be imported by passing their names to the `modules` argument.

### Worker and host assignment
Worker assignment function can be changed by passing [`common.assignWorker`](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/common.py#L197) to `nextWorker` argument of builder configurations.
By default worker will be chosen from the list of workernames for this build. List of available workers can be narrowed down to workers from a specific host be setting a desired host's address as a `host` property of build.
That way only workers from specified host will be eligible for that build.

[`common.assignBestHost`](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/common.py#L212) can be used to assign optimal host for a build. It returns host with the least instances of this build running.

## Schedulers
The schedulers are in the [master/maxscale/schedulers](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers). Schedulers describe the launch methods of builders.

* For the **manual launch** of builder use the `schedulers.ForceScheduler`. In parameters you can specify properties and repository information in `codebases` (for example, [build scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build.py)).

* To **launch a builder from another builder**, you must create a `schedulers.Triggerable` (for example, [build scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build.py)).

* `schedulers.SingleBranchScheduler` is used to start a build which **follows a commit to a remote repository**. `change_filter` can be specified to filter incoming changes (for example, [build_and_test_snapshot scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build_and_test_snapshot.py)).

* **Nightly build** can be started at a specific time of a day through `scheduler.Nightly` scheduler (see [nightly build_all scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build_all.py)).

See [Schedulers configuration official docs](http://docs.buildbot.net/current/manual/cfg-schedulers.html).

## Change Source

The Change Source component is responsible for configuring the tracking of changes in the repository. To monitor changes in the Maxscale repository, the GitPoller component is configured with a given function that restricts the list of branches that are followed by shadowing (see [master/maxscale/change_source/maxscale.py](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/change_source/maxscale.py)).

See [Change Source configuration official docs](http://docs.buildbot.net/current/manual/cfg-changesources.html).

## Auth

The project implements authorization of users via the account on the Github. The authorization configuration is described in the [master/maxscale/auth/github_auth.py
](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/auth/github_auth.py) component. 

Register the Github OAuth application on the https://github.com/settings/developers

See [Authentication plugins official docs](http://docs.buildbot.net/current/manual/cfg-www.html#web-authentication).

## Services

Directory: [master/maxscale/services](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/services/build.py)
The service components describe the rules for sending email-notifications to each builder.

See [Reporters configuration official docs](http://docs.buildbot.net/current/manual/cfg-reporters.html).
