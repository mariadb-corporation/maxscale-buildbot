import sys
import builtins
import importlib
from importlib.abc import Loader


class ReLoader(Loader):

    def create_module(self, spec):
        pass

    def exec_module(self, module):
        pass


modules = {}
