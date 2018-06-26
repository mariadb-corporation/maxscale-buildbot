# [[[section imports]]]
from paver.easy import *
import os
# [[[endsection]]]


# [[[section check configuration]]]
@task
def check_config():
    """Check configuration of BuildBot master"""
    sh("buildbot checkconfig .", cwd='master')
# [[[endsection]]]


# [[[section check python code with pycodestyle]]]
@task
def check_code():
    """Check python code according to static code checkers"""
    sh("pycodestyle pavement.py master/master.cfg master/maxscale")
# [[[endsection]]


# [[[section run the buildbot in development mode]]
@task
@cmdopts([
    ("command=", "c", "BuildBot master command to run, i.e. start, restart")
])
def buildbot(options, info):
    """Run buildot master in the development environment"""
    params = options["buildbot"]
    if "command" not in params:
        info("Please specify command to run with -c flag.")
        return
    buildbot_command = "buildbot {0} master".format(params["command"])
    environment = os.environ.copy()
    environment.update({"BUILDBOT_ENV": "development"})
    sh(buildbot_command, env=environment)
# [[[endsection]]]

# [[[section restart buildbot and development-worker]]]
@task
def restart_buildbot():
    """Restart both buildbot and corresponding worker"""
    call_task('check_config')
    call_task("buildbot", options={"command": "restart"})
    sh("buildbot-worker restart worker-dev")
# [[[endsection]]]
