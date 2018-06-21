from buildbot.plugins import util
from maxscale.config import constants


def maxscale_codebase():
    return util.CodebaseParameter(
        "",
        label="Main repository",
        branch=util.StringParameter(name="branch", default="develop"),
        revision=util.FixedParameter(name="revision", default=""),
        project=util.FixedParameter(name="project", default=""),
        repository=util.StringParameter(name="repository",
                                        default=constants.MAXSCALE_REPOSITORY),
    )
