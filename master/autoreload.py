import os
import sys
from importlib.abc import Loader
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location


class ReMetaPathFinder(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
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
        with open(module.__file__, "r") as file:
            code = file.read()
            if module.__name__ == __name__:
                module.__dict__.update({"maxscale_modules": maxscale_modules})
            exec(code, module.__dict__)
        maxscale_modules.append(module.__name__)
        return module


def install():
    for cls in sys.meta_path:
        if isinstance(cls, ReMetaPathFinder):
            del cls

    while maxscale_modules:
        mod = maxscale_modules.pop()
        if mod in sys.modules:
            del sys.modules[mod]
        else:
            print("{} not in the sys.modules".format(mod))

    sys.meta_path.insert(0, ReMetaPathFinder())


maxscale_modules = globals().get("maxscale_modules") or [__name__]


"""
import builtins


real_import = builtins.__import__


def _import(name, globals=None, locals=None, fromlist=(), level=0):
    print(name)
    return real_import(name, globals, locals, fromlist, level)


builtins.__import__ = _import
"""
