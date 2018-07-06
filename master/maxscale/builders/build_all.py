from buildbot.config import BuilderConfig
from buildbot.plugins import util, steps
from maxscale import workers
from maxscale.config import constants


ENVIRONMENT = {
    "JOB_NAME": util.Property("buildername"),
    "BUILD_ID": util.Interpolate('%(prop:buildnumber)s'),
    "BUILD_NUMBER": util.Interpolate('%(prop:buildnumber)s'),
    "MDBCI_VM_PATH": util.Property('MDBCI_VM_PATH'),
    "target": util.Property('target'),
    "cmake_flags": util.Property('cmake_flags'),
    "do_not_destroy_vm": util.Property('do_not_destroy_vm'),
    "build_experimental": util.Property('build_experimental'),
    "try_already_running": util.Property('try_already_running'),
    "run_upgrade_test": util.Property('run_upgrade_test'),
    "old_target": util.Property('old_target'),
    "ci_url": util.Property('ci_url')
}


def getCheckboxProperty(box):
    """Returns Property object from a nested parameter for a given box"""
    @util.renderer
    def getCheckbox(properties):
        nested_boxes = properties.getProperty("build_box_checkbox_container")
        return nested_boxes["{}_box".format(box)]

    return getCheckbox


def createBuildFactory():
    """
    Creates build factory containing steps
    which triggers build scheduler for each chosen box
    """
    factory = util.BuildFactory()
    for box in constants.BOXES:
        factory.addStep(steps.Trigger(
            name=box,
            schedulerNames=['build_all_subtask'],
            haltOnFailure=True,
            alwaysRun=True,
            waitForFinish=False,
            doStepIf=getCheckboxProperty(box),
            copy_properties=[
                "name",
                "repository",
                "branch",
                "target",
                "build_experimental",
                "product",
                "version",
                "cmake_flags"
                "do_not_destroy_vm",
                "try_already_running",
                "test_set",
                "ci_url",
                "smoke",
                "big"],
            set_properties={'box': box}
        ))
    return factory


BUILDERS = [
    BuilderConfig(
        name="build_all",
        workernames=workers.workerNames(),
        factory=createBuildFactory(),
        tags=["build"],
        env=ENVIRONMENT
    )
]
