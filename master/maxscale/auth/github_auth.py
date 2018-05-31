from buildbot.plugins import util
from maxscale.config.github_client_config import github_client_config
from maxscale.config.auth_config import auth_config


SETTINGS = {
    'auth': util.GitHubAuth(github_client_config['client_id'], github_client_config['client_secret']),
    'authz': util.Authz(
        allowRules=[
            util.AnyEndpointMatcher(role="admins"),
            util.AnyControlEndpointMatcher(role="admins", defaultDeny=False)
        ],
        roleMatchers=[
            util.RolesFromUsername(roles=["admins"], usernames=auth_config['admins'])
        ]
    )
}
