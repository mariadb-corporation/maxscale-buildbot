import inspect
import re
from buildbot.plugins import steps, util
from buildbot.interfaces import IRenderable
from zope.interface import implementer


def createScriptFileName(stepName):
    """Convert step name into a valid file name"""
    parts = stepName.split(' ')
    nonEmptyParts = filter(lambda part: part != "", parts)
    return "_".join(nonEmptyParts)


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
        code.append("# -*- coding: utf-8 -*-")
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
