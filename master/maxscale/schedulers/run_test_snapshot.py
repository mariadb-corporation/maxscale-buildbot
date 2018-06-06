import os
from buildbot.plugins import util, schedulers
from maxscale.config import constants


REPOSITORY_SCHEDULER = schedulers.Triggerable(
    name="run_test_snapshot",
    builderNames=["run_test_snapshot"],
    properties={
        "name": "test01",
        "branch": "master",
        "repository": constants.MAXSCALE_REPOSITORY,
        "target": "develop",
        "box": constants.BOXES[0],
        "product": 'mariadb',
        "version": constants.DB_VERSIONS[0],
        "test_set": "-LE HEAVY",
        "ci_url": constants.CI_SERVER_URL,
        "smoke": "yes",
        "big": "yes",
        "backend_ssl": 'no',
        "logs_dir": os.environ['HOME'] + "/LOGS",
        "template": 'default',
        "snapshot_name": 'clean',
        "test_branch": 'master',
    }
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_test_snapshot_force",
    builderNames=["run_test_snapshot"],
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
        util.StringParameter(name="snapshot_name", label="Snapshot name", size=50, default="clean"),
        util.StringParameter(name="target", label="Target", size=50, default="develop"),
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
            default="no"),
        util.StringParameter(name="logs_dir",
                             label="Logs dir",
                             size=50,
                             default=os.environ['HOME'] + "/LOGS"),
        util.ChoiceStringParameter(
            name="template",
            label="Template",
            choices=['default', 'nogalera', 'twomaxscales'],
            default='default'),
        util.StringParameter(name="test_branch", label="Test branch", size=100, default="master"),
    ]
)

SCHEDULERS = [REPOSITORY_SCHEDULER, MANUAL_SCHEDULER]
