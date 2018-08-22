import os
import sys
from importlib.abc import Loader
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location


class ReMetaPathFinder(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        """
        Seeks for module's files and passes spec to ReLoader
        if found files are submodules of maxscale module
        :param fullname: Name of the module
        :param path: Path to the module's files
        :param target:
        :return:
        """
        print(fullname)
        if not (fullname.startswith("maxscale") or fullname is __name__):
            return None
        if not path:
            path = [os.getcwd()]
        if "." in fullname:
            *parents, name = fullname.split(".")
        else:
            name = fullname
        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                filename = os.path.join(entry, name + ".py")
                submodule_locations = None
            if not os.path.exists(filename):
                continue
            return spec_from_file_location(fullname, filename, loader=ReLoader(),
                                           submodule_search_locations=submodule_locations)
        return None


class ReLoader(Loader):

    def exec_module(self, module):
        """
        Executes module's source code and tracks executed module
        :param module: Module to execute
        :return: Module
        """
        with open(module.__file__, "r") as file:
            code = file.read()
            if module.__name__ == __name__:
                module.__dict__.update({"maxscale_modules": _maxscaleModules})
            exec(code, module.__dict__)
        _maxscaleModules.append(module.__name__)
        return module


def install():
    """
    Installs new ReMetaPathFinder to sys.meta_path
    :return:
    """
    for cls in sys.meta_path:
        if isinstance(cls, ReMetaPathFinder):
            del cls

    while _maxscaleModules:
        mod = _maxscaleModules.pop()
        if mod in sys.modules:
            del sys.modules[mod]
        else:
            print("{} not in the sys.modules".format(mod))

    sys.meta_path.insert(0, ReMetaPathFinder())


# Stores loaded maxscale modules
_maxscaleModules = globals().get("maxscale_modules") or [__name__]

