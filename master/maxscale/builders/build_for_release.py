from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from buildbot.steps.trigger import Trigger
from maxscale.builders.build import ENVIRONMENT
from maxscale.config import constants
from maxscale import workers

COMMON_PROPERTIES = [
    "name",
    'branch',
    "repository",
    "build_experimental",
    "version_number",
    "old_target",
    "host",
    "owner",
    "owners",
]

BUILD_TARGETS = [
    {
        "target_name": "release",
        "cmake_flags": "-DBUILD_TESTS=N -DBUILD_MMMON=Y -DBUILD_CDC=Y -DWITH_ASAN=Y"
    },
    {
        "target_name": "debug",
        "cmake_flags": "-DBUILD_TESTS=Y -DCMAKE_BUILD_TYPE=Debug -DBUILD_MMMON=Y -DBUILD_CDC=Y -DWITH_ASAN=Y"
    }
]


class BuildForReleaseTrigger(Trigger):
    """
    Implements custom trigger step which triggers 'build_all'
    task for every build target
    """
    def getSchedulersAndProperties(self):
        """
        Overrides method getSchedulersAndProperties of Trigger class
        so that it returns a scheduler for every build target
        :return: List which contains schedulers for every build target
        """
        schedulers = []
        for buildTarget in self.set_properties["build_targets"]:
            propertiesToSet = {}
            propertiesToSet.update(self.set_properties)
            propertiesToSet.update(buildTarget)
            propertiesToSet["virtual_builder_name"] = \
                "Build all for {}".format(buildTarget["target_name"])
            propertiesToSet["target"] = "maxscale-{}-{}".format(
                self.set_properties["version_number"],
                buildTarget["target_name"])
            for schedulerName in self.schedulerNames:
                schedulers.append({
                    "sched_name": schedulerName,
                    "props_to_set": propertiesToSet,
                    "unimportant": schedulerName in self.unimportantSchedulerNames
                })

        return schedulers


def createBuildSteps():
    buildSteps = []
    buildSteps.append(BuildForReleaseTrigger(
        name="build_for_release",
        schedulerNames=["build_all_triggerable"],
        waitForFinish=True,
        copy_properties=COMMON_PROPERTIES,
        set_properties={
            "build_targets": BUILD_TARGETS,
            "run_upgrade_test": "yes",
            "ci_url": constants.CI_SERVER_URL,
            "repo_path": "repository",
            "do_not_destroy_vm": "no"
        }
    ))
    return buildSteps


def createBuildFactory():
    factory = util.BuildFactory()
    buildSteps = createBuildSteps()
    factory.addSteps(buildSteps)
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_for_release",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT
    )
]
