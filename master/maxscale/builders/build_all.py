from buildbot.config import BuilderConfig
from buildbot.plugins import util
from buildbot.steps.trigger import Trigger
from maxscale import workers
from maxscale.builders.support import common
from maxscale.config import constants
from .build import ENVIRONMENT


class BuildAllTrigger(Trigger):
    """
    Implements custom trigger step which triggers 'build' task on a virtual builder for every marked checkbox
    """
    def getSchedulersAndProperties(self):
        """
        Overrides method getSchedulersAndProperties of Trigger class
        so that it returns a scheduler for every marked checkbox
        :return: List which contains schedulers for every marked checkbox
        """
        schedulers = []
        for checkboxName, checkboxValue in self.set_properties["build_box_checkbox_container"].items():
            if checkboxValue:
                propertiesToSet = {}
                propertiesToSet.update(self.set_properties)
                propertiesToSet.update({"box": checkboxName})
                propertiesToSet.update({"virtual_builder_name":
                                        "{}_{}".format(self.set_properties["virtual_builder_name"], checkboxName)})
                for schedulerName in self.schedulerNames:
                    schedulers.append({
                        "sched_name": schedulerName,
                        "props_to_set": propertiesToSet,
                        "unimportant": schedulerName in self.unimportantSchedulerNames
                    })

        return schedulers


def createBuildFactory():
    """
    Creates build factory containing steps
    which triggers build scheduler for each chosen box
    """
    factory = util.BuildFactory()
    factory.addStep(BuildAllTrigger(
        name="build_all",
        schedulerNames=['build'],
        waitForFinish=True,
        copy_properties=[
            "name",
            "repository",
            "branch",
            "build_box_checkbox_container",
            "target",
            "build_experimental",
            "product",
            "version",
            "cmake_flags",
            "do_not_destroy_vm",
            "try_already_running",
            "test_set",
            "ci_url",
            "smoke",
            "big",
            "host",
            "owner",
            "owners",
        ],
        set_properties={
            "virtual_builder_name": "build"
        }
    ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_all",
        workernames=workers.workerNames(),
        nextWorker=common.assignWorker,
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT,
        collapseRequests=False
    )
]
