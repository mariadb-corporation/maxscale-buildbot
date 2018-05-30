import os
from buildbot.plugins import util, schedulers
from maxscale.config import constants


REPOSITORY_SCHEDULER = schedulers.Triggerable(
    name="run_test",
    builderNames=["run_test"],
    properties={
        "name": "test01",
        "branch": "master",
        "repository": constants.MAXSCALE_REPOSITORY,
        "target": "develop",
        "box": constants.BOXES[0],
        "product": 'mariadb',
        "version": constants.DB_VERSIONS[0],
        "do_not_destroy_vm": 'no',
        "test_set": "-LE HEAVY",
        "ci_url": constants.CI_SERVER_URL,
        "smoke": "yes",
        "big": "yes",
        "backend_ssl": 'no',
        "use_snapshots": 'no',
        "logs_dir": os.environ['HOME'] + "/LOGS",
        "no_vm_revert": 'no',
        "template": 'default',
    }
)

MANUAL_SCHEDULER = schedulers.ForceScheduler(
    name="run_test_force",
    builderNames=["run_test"],
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
            default="no"),
        util.ChoiceStringParameter(
            name="use_snapshots",
            label="Use snapshots",
            choices=["no", "yes"],
            default="no"),
        util.StringParameter(name="logs_dir", label="Logs dir", size=50, default=os.environ['HOME'] + "/LOGS"),
        util.ChoiceStringParameter(
            name="no_vm_revert",
            label="No vm revert",
            choices=["no", "yes"],
            default="no"),
        util.ChoiceStringParameter(
            name="template",
            label="Template",
            choices=['default', 'nogalera', 'twomaxscales'],
            default='default'),
        util.StringParameter(name="config_to_clone", label="Config to clone", size=50),
    ]
)

SCHEDULERS = [REPOSITORY_SCHEDULER, MANUAL_SCHEDULER]
