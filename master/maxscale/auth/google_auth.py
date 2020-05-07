from buildbot.plugins import util
from maxscale.config.google_auth_config import GOOGLE_AUTH_CONFIG


SETTINGS = {
    'auth': util.GoogleAuth(GOOGLE_AUTH_CONFIG['client_id'],
                            GOOGLE_AUTH_CONFIG['client_secret']),
    'authz': util.Authz(
        allowRules=[
            util.AnyEndpointMatcher(role="admins"),
            util.AnyControlEndpointMatcher(role="admins", defaultDeny=False)
        ],
        roleMatchers=[
            util.RolesFromDomain(admins=["mariadb.com"])
        ]
    )
}

