from buildbot.www.plugin import Application

# create the interface for the setuptools entry point
ep = Application(__name__, "Buildbot Maxscale plugin", ui=True)