#!/usr/bin/python3

""""
This module is a wrapper for the buildbot-worker that emulates the execution inside the virtual environment.
This script must lay along with the buildbot-worker executable in the virtual environment bin directory.
"""

import os
import subprocess
import sys

bin_path = os.path.dirname(os.path.realpath(__file__))
virtual_env_path = os.path.abspath("{}/..".format(bin_path))

environment = os.environ.copy()
environment["PATH"] = "{}:{}".format(bin_path, environment["PATH"])
environment["VIRTUAL_ENV"] = virtual_env_path

command = sys.argv.copy()
command[0] = "{}/buildbot-worker".format(bin_path)

result = subprocess.call(command, env=environment)
exit(result)
