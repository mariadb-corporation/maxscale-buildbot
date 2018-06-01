from buildbot.plugins import util
from maxscale.config.github_client_config import GITHUB_CLIENT_CONFIG
from maxscale.config.auth_config import AUTH_CONFIG


SETTINGS = {
    'auth': util.GitHubAuth(GITHUB_CLIENT_CONFIG['client_id'], GITHUB_CLIENT_CONFIG['client_secret']),
    'authz': util.Authz(
        allowRules=[
            util.AnyEndpointMatcher(role="admins"),
            util.AnyControlEndpointMatcher(role="admins", defaultDeny=False)
        ],
        roleMatchers=[
            util.RolesFromUsername(roles=["admins"], usernames=AUTH_CONFIG['admins'])
        ]
    )
}
