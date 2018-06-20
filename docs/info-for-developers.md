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
In some builders, dicts `DEFAULT_PROPERTIES` with the default values are declared for the builder properties (for example, [Build builder](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py)). `DEFAULT_PROPERTIES` is used if any property of the builder at launch is not specified. For specify default properties, builder use [master/maxscale/builders/common.SetDefaultPropertiesStep](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/common.py), which sets the missing properties to the default value.

### Custom Build Step
In some builders, to specify a group of properties in one step, you can use your own class, inherited from `steps.BuildStep` ([Custom Buildsteps docs](http://docs.buildbot.net/current/manual/customization.html#writing-new-buildsteps)). For example,  [Build builder](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py) use own BuildSetPropertiesStep class for it.

### Shell-scripts
To use the shell script in the build, you need to place it in the directory [master/shell_scripts](https://github.com/mariadb-corporation/maxscale-buildbot/tree/master/master/shell_scripts). Next, in the builder, you need to add a trigger step to call the `download_shell_scripts` builder.

Example:
```python
factory.addStep(steps.Trigger(
    name="Call the 'download_shell_scripts' scheduler",
    schedulerNames=['download_shell_scripts'],
    copy_properties=['SHELL_SCRIPTS_PATH']
))
```

`SHELL_SCRIPTS_PATH` - destination path on the worker.

See [Builder configuration official docs](http://docs.buildbot.net/current/manual/cfg-builders.html) and [Build Steps official docs](http://docs.buildbot.net/current/manual/cfg-buildsteps.html).

## Schedulers
The schedulers are in the [master/maxscale/schedulers](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers). Schedulers describe the launch methods of builders.

* For the **manual launch** of builder use the `schedulers.ForceScheduler`. In parameters you can specify properties and repository information in `codebases` (for example, [build scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build.py)).

* For **launch a builder from another builder**, you must create a `schedulers.Triggerable` (for example, [build scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build.py)).

* For launch the builder by the event of **detecting changes in the repository**, you must create a `schedulers.SingleBranchScheduler` with the specified `change_filter` (for example, [build_and_simple_test scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build_and_simple_test.py)).

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
