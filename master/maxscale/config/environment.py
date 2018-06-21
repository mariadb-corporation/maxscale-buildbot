import os


def is_development():
    """Check whether the application is running in development environment or not"""
    return ('BUILDBOT_ENV' in os.environ) and (os.environ['BUILDBOT_ENV'] == 'development')
