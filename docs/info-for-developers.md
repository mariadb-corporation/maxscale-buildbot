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
* Automatic module loader

## Builders

The builders are in the [master/maxscale/builders](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders). Builders describe the steps of the task.

### Default properties
In some builders, dicts `DEFAULT_PROPERTIES` with the default values are declared for the builder properties (for example, [Build builder](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py)). `DEFAULT_PROPERTIES` is used if any property of the builder at launch is not specified. To specify default properties, builder uses [master/maxscale/builders/common.SetDefaultPropertiesStep](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/common.py), which sets the missing properties to the default value.

### Environmental variables on the remote worker
Each worker has its separate environment. To create environmental variable on worker a dictionary with variable's name and value must be created and passed to `env` property of the builder's configuration.
[Dictionary with environmental variables](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py#L8) can render build's properties as variable's value to pass properties to worker's environment.
Alternatively master's environment can be copied to worker by assigning `dict(os.environ))` to the `env` argument of builder's configuration.

### Custom Build Step
In some builders, to specify a group of properties in one step, you can use your own class, inherited from `steps.BuildStep` ([Custom Buildsteps docs](http://docs.buildbot.net/current/manual/customization.html#writing-new-buildsteps)). For example, [Build builder](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build.py) uses own BuildSetPropertiesStep class for it.

### Remote Python scripts
Python functions can be executed on a worker using [maxscale.builders.support.support.executePythonScript(name, function, modules=(), **kwargs)](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/support.py#L50) function. This functions will transform Python function into a string and transfer it to `<builddir>/build/script` directory on the remote worker.
All build's properties are imported to the script as a local variables. Following modules are imported by default: sys, os, os.path, shutil, subprocess and additional modules can be imported by passing their names to the `modules` argument.

### Worker and host assignment
Worker assignment function can be changed by passing [`common.assignWorker`](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/common.py#L197) to `nextWorker` argument of builder configurations.
By default worker will be chosen from the list of workernames for this build. List of available workers can be narrowed down to workers from a specific host be setting a desired host's address as a `host` property of build.
That way only workers from specified host will be eligible for that build.

### Dynamic Trigger
Sometimes it is necessary to run large amount of instances of single task each with different set of properties but on the same codebase. To do this from a single trigger step [Dynamic Trigger](http://docs.buildbot.net/current/manual/cfg-buildsteps.html#dynamic-trigger) can be used.
You need to create a class which inherits Buildbot's `Trigger` step and define a method `getSchedulersAndProperties` in it. The method must return a list of objects where each objects must contain name of a triggered build, its properties and if this build is important.
An example of such function can be seen in the implementation of [Build All](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/build_all.py#L10) task. At the time of execution all existing property of the initial build can be accessed from within this function using `get_properties` method.
Multiple builds request created this way can be automatically collapsed by Buildbot so it is recommended to disable request collapse in the triggered build settings using `collapseRequests` argument.

Every build which was triggered this way will be displayed in the same step of initial builds but but as separate builds on the 'Builders' page of WEB UI. To hide triggered builds from UI `virtual_builder_name` property must be set.

[`common.assignBestHost`](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/builders/support/common.py#L212) can be used to assign optimal host for a build. It returns host with the least instances of this build running.

## Schedulers
The schedulers located in the [master/maxscale/schedulers](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers) directory. Schedulers acts as a build launchers.

* For the **manual launch** of builder use the `schedulers.ForceScheduler`. You can specify builds's properties in `properties` argument and repository information in `codebases` (for example, [build scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build.py)).

* To **launch a builder from another builder**, you must create a `schedulers.Triggerable` (for example, [build scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build.py)).

* `schedulers.SingleBranchScheduler` is used to start a build which **follows a commit to a remote repository**. `change_filter` can be specified to filter incoming changes (for example, [build_and_test_snapshot scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build_and_test_snapshot.py)).

* **Nightly build** can be started at a specific time of a day through `scheduler.Nightly` scheduler (see [nightly build_all scheduler](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/build_all.py)).

See [Schedulers configuration official docs](http://docs.buildbot.net/current/manual/cfg-schedulers.html).

### Schedulers properties

Scheduler properties are parameters that will be passed to builds launched by this scheduler. They can be defined in two different forms: a list of objects derived from [`BaseParameter`](http://docs.buildbot.net/current/manual/cfg-schedulers.html#nestedparameter) class (those are provided by the Buildbot) and a dictionary with parameter name as a key.

The first one can be used solely for manual scheduler, like `ForceScheduler`. Each parameter will have its own editable field in the WEB UI and can store a default value for it.
All of the MaxScale Buildbot properties of this kind are stored in the [`properties`](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/properties.py) module in the `scheduler` subdirectory.
This module also provides [function](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/schedulers/properties.py#L205) which extracts default values from the pre-defined list of parameters and builds a dictionary with property name as a key and its default value as value.
This allows to define a single list of properties for manual scheduler and create a corresponding dictionary for automatic counterpart of this scheduler, if they share the same set of properties.

Properties in the second form are defined for every automatic scheduler. Its a simple dictionary with keys and values with the restriction that all values must be defined at runtime.
That means `Deferred` objects are not allowed as a values. And if property needs to be set at the start of a build than it should be done in one of build steps. Buildbot provides multiple [steps](http://docs.buildbot.net/current/manual/cfg-buildsteps.html#setting-properties) for that purpose.

## Change Source

The Change Source component is responsible for configuration of a repository tracker. To monitor changes in the Maxscale repository, the GitPoller component is configured with a given function that restricts the list of branches that are followed by shadowing (see [master/maxscale/change_source/maxscale.py](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/change_source/maxscale.py)).

See [Change Source configuration official docs](http://docs.buildbot.net/current/manual/cfg-changesources.html).

## Auth

The project implements authorization of users via the account on the Github. The authorization configuration is described in the [master/maxscale/auth/github_auth.py](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/auth/github_auth.py) component. 

Register the Github OAuth application on the https://github.com/settings/developers

See [Authentication plugins official docs](http://docs.buildbot.net/current/manual/cfg-www.html#web-authentication).

## Services

Directory: [master/maxscale/services](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/maxscale/services/build.py)
The service components describe the rules for sending email-notifications to each builder. Each must subscribe to a builder and provide a valid form for composing email.

### ExpandedStepsFormatter
By default Buildbot provides build context only for steps of the main build without providing data on triggered builds.
ExpandedStepsFormatter looks directly through database for additional data on triggered build's steps using Buildbot's [DATA API](http://docs.buildbot.net/current/developer/data.html)


## Automatic module loader
Buildbot provides ability to reload configuration without restarting master using `buildbot reconfig master` command. However only main configuration file `master.cfg` is reloaded.
Module [autoreloader.py](https://github.com/mariadb-corporation/maxscale-buildbot/blob/master/master/autoreload.py) removes all previously imported and tracked modules from `sys.modules` list which allows them to be reloaded on the next import.
`autoreload.py` must be imported and installed to the main config file before importing any other modules. After that it tracks all imported modules from `maxscale` module. That means it does not reload any Python or Buildbot module as some of this module are not designed to be reloaded and can behave unpredictably.

See [Reporters configuration official docs](http://docs.buildbot.net/current/manual/cfg-reporters.html).
