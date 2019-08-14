from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from buildbot.steps.trigger import Trigger
from maxscale.builders.build import ENVIRONMENT
from maxscale.builders.support import common
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
    "owners",
]

BUILD_TARGETS = [
    {
        "target_name": "release",
        "cmake_flags": "-DBUILD_TESTS=N -DBUILD_MMMON=Y -DBUILD_CDC=Y"
    },
    {
        "target_name": "debug",
        "cmake_flags": "-DBUILD_TESTS=Y -DCMAKE_BUILD_TYPE=Debug -DBUILD_MMMON=Y -DBUILD_CDC=Y"
    }
]


@util.renderer
def getMajorVersion(properties):
    """
    Returns major version, extracted it from version_number property
    :param properties:
    :return: Major version
    """
    versionNumber = properties.getProperty("version_number")
    return ".".join(versionNumber.split('.')[:2])


@util.renderer
def constructTargetString(properties):
    """
    Returns target
    :param properties:
    :return: Target
    """
    majorVersion = getMajorVersion(properties)
    return '{}-all-versions'.format(majorVersion)


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
    factory.addStep(steps.Trigger(
        name="Call the 'create_full_repo_all' scheduler",
        schedulerNames=['create_full_repo_all_triggerable'],
        waitForFinish=True,
        copy_properties=[
            "branch",
            "repository",
            "host",
            "owners",
            "version",
        ],
        set_properties={
            "major_ver": getMajorVersion,
            "target": constructTargetString
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_for_release",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        nextBuild=common.assignBuildRequest,
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT
    )
]
