# -*- python -*-
# ex: set filetype=python:

import autoreload

autoreload.ModuleTracker().install()

from buildbot.plugins import secrets
import os
from maxscale.builders import MAXSCALE_BUILDERS
from maxscale.config import environment
from maxscale.schedulers import MAXSCALE_SCHEDULERS
from maxscale.services import MAXSCALE_SERVICES
from maxscale.auth import MAXSCALE_AUTH
from maxscale.change_source import MAXSCALE_POLLERS
from maxscale import workers
from maxscale.config.database_config import DATABASE_CONFIG

# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c = BuildmasterConfig = {}

# WORKERS

c['workers'] = workers.workerConfiguration()
c['protocols'] = {'pb': {'port': 9989}}

# CHANGESOURCES

if not environment.is_development():
    c['change_source'] = MAXSCALE_POLLERS

# SCHEDULERS

c['schedulers'] = MAXSCALE_SCHEDULERS

# BUILDERS

c['builders'] = MAXSCALE_BUILDERS

# BUILDBOT SERVICES

c['services'] = MAXSCALE_SERVICES

# SECRET PROVIDERS
currentDirectory = os.path.dirname(os.path.realpath(__file__))
secretsDirectory = os.path.join(currentDirectory, "maxscale/config/secrets")
c['secretsProviders'] = [
    secrets.SecretInAFile(dirname=secretsDirectory),
]

# PROJECT IDENTITY

c['title'] = "MaxScale CI"
c['titleURL'] = "https://github.com/mariadb-corporation/maxscale-buildbot"
c['buildbotURL'] = "https://maxscale-ci.mariadb.com/"
if environment.is_development():
    c['buildbotURL'] = "http://localhost:8010/"

# Web intefrace configuration
c['www'] = dict(
    port="tcp:8010:interface=127.0.0.1",
    plugins=dict(waterfall_view={}, console_view={}, grid_view={}),
)
# Do not enable authentication or authorization during the development
if not environment.is_development():
    c['www'].update(dict(
        auth=MAXSCALE_AUTH['auth'],
        authz=MAXSCALE_AUTH['authz']))

# DB URL
if environment.is_development():
    c['db'] = {
        'db_url': "sqlite:///state.sqlite",
    }
else:
    c['db'] = {
        'db_url': "mysql+mysqldb://{username}:{password}@{hostname}/{database}".format(**DATABASE_CONFIG)
    }

# Configure privacy settings, http://docs.buildbot.net/latest/manual/cfg-global.html#buildbotnetusagedata
c['buildbotNetUsageData'] = 'basic'
