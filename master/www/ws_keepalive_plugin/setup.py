#!/usr/bin/env python

try:
    from buildbot_pkg import setup_www_plugin
except ImportError:
    import sys
    print('Please install buildbot_pkg module in order to install that '
          'package, or use the pre-build .whl modules available on pypi',
          file=sys.stderr)
    sys.exit(1)

setup_www_plugin(
    name='buildbot-ws-keepalive-plugin',
    description='Make websocket keepalive requests',
    author=u'Evgeny Vlasov',
    author_email=u'evgeny.vlasov@fruct.org',
    url='https://github.com/mariadb-corporation/maxscale-buildbot',
    packages=['buildbot_ws_keepalive_plugin'],
    package_data={
        '': [
            'VERSION',
            'static/*'
        ]
    },
    entry_points="""
        [buildbot.www]
        ws_keepalive_plugin = buildbot_ws_keepalive_plugin:ep
    """,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
    ],
)
