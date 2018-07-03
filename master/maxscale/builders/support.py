import os
import inspect
import re
from buildbot.plugins import steps, util
from buildbot.interfaces import IRenderable
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
    __defaultModules = set(["sys", "os", "os.path", "shutil"])

    def __init__(self, function, modules=()):
        self.__function = function
        self.__modules = self.__defaultModules.union(modules)

    def getRenderingFor(self, properties):
        """Construct remote Python script"""
        code = ["#!/usr/bin/env python3"]
        code.extend(self.__renderModules())
        code.extend(self.__renderProperties(properties))
        code.extend(self.__convertFunctionToStrings())
        return "\n".join(code)

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
