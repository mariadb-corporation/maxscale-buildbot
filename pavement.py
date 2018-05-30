# [[[section imports]]]
from paver.easy import *
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
    sh("pycodestyle pavement.py master/master.cfg master/config")
# [[[endsection]]
