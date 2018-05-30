from buildbot.plugins import util, schedulers
from maxscale.config import constants


MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="build_and_test",
    label="Build and test",
    builderNames=["build_and_test"],
    codebases=[
        util.CodebaseParameter(
            "",
            label="Main repository",
            branch=util.StringParameter(name="branch", default="develop"),
            revision=util.FixedParameter(name="revision", default=""),
            project=util.FixedParameter(name="project", default=""),
            repository=util.StringParameter(name="repository",
                                            default=constants.MAXSCALE_REPOSITORY),
        ),
    ],
    properties=[
        util.StringParameter(name="name", label="Name of this build", size=50, default="test01"),
        util.StringParameter(name="target", label="Target", size=50, default="develop"),
        util.ChoiceStringParameter(
            name="build_experimental",
            label="Build experimental",
            choices=["yes", "no"],
            default="yes"),
        util.ChoiceStringParameter(
            name="box",
            label="Box",
            choices=constants.BOXES,
            default=constants.BOXES[0]),
        util.ChoiceStringParameter(
            name="product",
            label="Product",
            choices=['mariadb', 'mysql'],
            default='mariadb'),
        util.ChoiceStringParameter(
            name="version",
            label="Version",
            choices=constants.DB_VERSIONS,
            default=constants.DB_VERSIONS[0]),
        util.StringParameter(name="cmake_flags", label="CMake flags", size=50,
                             default=constants.DEFAULT_CMAKE_FLAGS),
        util.ChoiceStringParameter(
            name="do_not_destroy_vm",
            label="Do not destroy vm",
            choices=['no', 'yes'],
            default='no'),
        util.StringParameter(name="test_set", label="Test set", size=50, default="-LE HEAVY"),
        util.StringParameter(name="ci_url", label="ci url", size=50,
                             default=constants.CI_SERVER_URL),
        util.ChoiceStringParameter(
            name="smoke",
            label="Run fast versions of every test",
            choices=["yes", "no"],
            default="yes"),
        util.ChoiceStringParameter(
            name="big",
            label="Use larger number of VMs",
            choices=["yes", "no"],
            default="yes"),
        util.ChoiceStringParameter(
            name="backend_ssl",
            label="Backend ssl",
            choices=["no", "yes"],
            default="no")
    ]
)

SCHEDULERS = [MANUAL_SCHEDULER]
