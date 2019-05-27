# How to create new tasks in BuildBot

## First step

First, create file in the `master/maxscale/builders/` directory with the name of the task being created, for example, `master/maxscale/builders/my_build.py`.

**Skeleton of the builder**:

```python
from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.builders.support import common, support


# TODO: List all the parameters required for the task, passed from the parent task or from the scheduler
ENVIRONMENT = {
    # Get the original value of property
    "parameter_name_1": util.Property("parameter_name_1"),
   
    # Construct new parameter with value of parameter_name_1. For example, if the value of
    # parameter_name_1 is `first-value`, value of the parameter_name_2
    # will be `first-value-version-2` 
    "parameter_name_2": util.Interpolate('%(prop:parameter_name_1)s-version-2')
}


# TODO: Define your own build steps as methods, which returns the array of builbot step objects
def customStep1():
    return [steps.ShellCommand(
        name="What step doing?",
        command=[util.Interpolate("%(prop:HOME)s/script.sh"), util.Property("parameter_name_1")],
        alwaysRun=True)]


# TODO: Extend buildSteps array with all required steps for this build
def createBuildSteps():
    buildSteps = []
    # Use common steps
    buildSteps.extend(common.getWorkerHomeDirectory())
    # And your own steps, defined above
    buildSteps.extend(customStep1())
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    factory.addSteps(createBuildSteps())
    return factory


BUILDERS = [
    BuilderConfig(
        # TODO: Set the builder name
        name="Name of the task",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        # TODO: Define the builder tags or pass empty array
        tags=["tag_1", "tag_2"],
        env=ENVIRONMENT,
        collapseRequests=False
    )
]
```

In next, add the created module to the `master/maxscale/builders/__init__.py`, for example:

```python
import itertools
from . import my_build

MAXSCALE_BUILDERS = list(itertools.chain(
    my_build.BUILDERS,
))
```

## Second step

Create file in the `master/maxscale/schedulers/` directory with the name of the task, for example, `master/maxscale/schedulers/my_build.py`.

**Skeleton of the scheduler**:

```python
from buildbot.plugins import schedulers
from maxscale.config import constants
from . import properties

# TODO: List all the parameters required for the task, passed to the child task
MY_BUILD_PROPERTIES = [
    properties.version_number(),
    properties.host(),
]

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    # TODO: Set the scheduler name
    name="my_build",
    # TODO: Set the builder name
    builderNames=["my_build"],
    # TODO: Set the button title
    buttonName="Publish Release",
    # TODO: Set the repository info
    codebases=properties.emptyCodebase() # in this case = [util.CodebaseParameter(codebase='', hide=True)]
    properties=MY_BUILD_PROPERTIES
)

SCHEDULERS = [MANUAL_SCHEDULER]
```

In next, add the created module to the `master/maxscale/schedulers/__init__.py`, for example:

```python
import itertools
from . import my_build


MAXSCALE_SCHEDULERS = list(itertools.chain(
    my_build.SCHEDULERS
))
```