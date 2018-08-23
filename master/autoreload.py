import sys
from importlib.abc import MetaPathFinder


class ModuleTracker(MetaPathFinder):

    # Stores loaded maxscale modules
    maxscaleModules = [__name__]

    def __init__(self):
        for pathfinder in sys.meta_path:
            if hasattr(pathfinder, "maxscaleModules"):
                self.maxscaleModules = pathfinder.maxscaleModules
                sys.meta_path.remove(pathfinder)
        super().__init__()

    def find_spec(self, fullname, path, target=None):
        """
        Tracks imported modules of maxscale project
        :param fullname: Name of the module
        :param path: Path to the module's files
        :param target:
        :return:
        """
        if fullname.startswith("maxscale") or fullname is __name__:
            self.maxscaleModules.append(fullname)

    def install(self):
        """
        Installs self into sys.meta_path
        :return:
        """
        self.clearMaxscaleModules()
        sys.meta_path.insert(0, self)

    def clearMaxscaleModules(self):
        """
        Deletes maxscale modules from the list of imported modules
        :return:
        """
        while self.maxscaleModules:
            mod = self.maxscaleModules.pop()
            if mod in sys.modules:
                del sys.modules[mod]
            else:
                print("{} not in the sys.modules".format(mod))
