from buildbot.steps.trigger import Trigger


class BuildAllTrigger(Trigger):
    """
    Implements custom trigger step which triggers 'build' task on a virtual builder for every marked checkbox
    """
    def __init__(self, schedulerNames=None, sourceStamp=None, sourceStamps=None,
                 updateSourceStamp=None, alwaysUseLatest=False,
                 waitForFinish=False, set_properties=None,
                 copy_properties=None, parent_relationship="Triggered from",
                 unimportantSchedulerNames=None, **kwargs):
        super().__init__(schedulerNames, sourceStamp, sourceStamps,
                         updateSourceStamp, alwaysUseLatest,
                         waitForFinish, set_properties,
                         copy_properties, parent_relationship,
                         unimportantSchedulerNames, **kwargs)

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
