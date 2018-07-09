import os
import inspect
import re
from buildbot.plugins import steps, util
from buildbot.interfaces import IRenderable
from buildbot.steps.trigger import Trigger
from zope.interface import implementer


# Following methods are internal and used to beautify the rest of the code above
def executeScript(name, script, args=(), haltOnFailure=True, flunkOnFailure=True, alwaysRun=False, env={}, **kwargs):
    """Download the executable script onto the worker and execute it"""
    shellScriptPath = util.Interpolate("%(prop:builddir)s/scripts/%(kw:fileName)s",
                                       fileName=createScriptFileName(name))

    kwargs["haltOnFailure"] = haltOnFailure
    kwargs["flunkOnFailure"] = flunkOnFailure
    kwargs["alwaysRun"] = alwaysRun

    downloadScript = steps.StringDownload(
        script,
        workerdest=shellScriptPath,
        name="Download script to the worker: {}".format(name),
        mode=0o755,
        **kwargs)

    runScript = steps.ShellCommand(
        name="Execute script: {}".format(name),
        command=[shellScriptPath, *args],
        env=env,
        **kwargs)

    kwargs["alwaysRun"] = True

    removeScript = steps.ShellCommand(
        name="Remove script from worker: {}".format(name),
        command=["rm", "-f", shellScriptPath],
        **kwargs)

    return [downloadScript, runScript, removeScript]


def createScriptFileName(stepName):
    """Convert step name into a valid file name"""
    parts = stepName.split(' ')
    nonEmptyParts = filter(lambda part: part != "", parts)
    return "_".join(nonEmptyParts)


def executePythonScript(name, function, modules=(), **kwargs):
    """Convert passed function to the text, prepend properties and execute in on the server"""
    return executeScript(name, PythonFunctionRenderer(function, modules), **kwargs)


@implementer(IRenderable)
class PythonFunctionRenderer(object):
    """
    This class converts the passed function to the self-sufficient Python application that
    can be transferred and run on the remote server.
    """
    __defaultModules = set(["sys", "os", "os.path", "shutil", "subprocess"])

    def __init__(self, function, modules=()):
        self.__function = function
        self.__modules = self.__defaultModules.union(modules)

    def getRenderingFor(self, properties):
        """Construct remote Python script"""
        code = ["#!/usr/bin/env python3"]
        code.extend(self.__renderModules())
        code.extend(self.__printScriptContents())
        code.extend(self.__renderProperties(properties))
        code.extend(self.__convertFunctionToStrings())
        return "\n".join(code)

    def __printScriptContents(self):
        """Method adds a code to print the script contents when running it"""
        return ["__script = open(sys.argv[0], \"r\")",
                "for number, line in enumerate(__script.readlines(), start=1):",
                "    print(\"{:>5}: {}\".format(number, line.rstrip()))",
                "__script.close()"]

    def __renderProperties(self, properties):
        """Get all the properties from the build and insert them into the remote code."""
        propertiesList = properties.asList()
        code = []
        for name, value, _ in propertiesList:
            code.append("{} = {}".format(name, repr(value)))
        return code

    def __renderModules(self):
        """Convert module names into proper import statements"""
        code = []
        for module in self.__modules:
            code.append("import {}".format(module))
        return code

    def __convertFunctionToStrings(self):
        """Extract function code using the inspect module, remove function name and shift lines to the left"""
        lines = inspect.getsource(self.__function)
        raw_code = lines.split("\n")[1:]
        offset = len(re.match(r"\s*", raw_code[0], re.UNICODE).group(0))
        code = []
        for line in raw_code:
            code.append(line[offset:])
        return code


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
