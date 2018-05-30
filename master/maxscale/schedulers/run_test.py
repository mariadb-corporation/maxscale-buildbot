import os
from buildbot.schedulers.forcesched import ChoiceStringParameter
from buildbot.schedulers.forcesched import CodebaseParameter
from buildbot.schedulers.forcesched import FixedParameter
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.forcesched import StringParameter
from buildbot.schedulers.triggerable import Triggerable
from maxscale.config import constants


REPOSITORY_SCHEDULER = Triggerable(
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

MANUAL_SCHEDULER = ForceScheduler(
    name="run_test_force",
    builderNames=["run_test"],
    codebases=[
        CodebaseParameter(
            "",
            label="Main repository",
            branch=StringParameter(name="branch", default="develop"),
            revision=FixedParameter(name="revision", default=""),
            project=FixedParameter(name="project", default=""),
            repository=StringParameter(name="repository",
                                       default=constants.MAXSCALE_REPOSITORY),
        ),
    ],
    properties=[
        StringParameter(name="name", label="Name of this build", size=50, default="test01"),
        StringParameter(name="target", label="Target", size=50, default="develop"),
        ChoiceStringParameter(
            name="box",
            label="Box",
            choices=constants.BOXES,
            default=constants.BOXES[0]),
        ChoiceStringParameter(
            name="product",
            label="Product",
            choices=['mariadb', 'mysql'],
            default='mariadb'),
        ChoiceStringParameter(
            name="version",
            label="Version",
            choices=constants.DB_VERSIONS,
            default=constants.DB_VERSIONS[0]),
        ChoiceStringParameter(
            name="do_not_destroy_vm",
            label="Do not destroy vm",
            choices=['no', 'yes'],
            default='no'),
        StringParameter(name="test_set", label="Test set", size=50, default="-LE HEAVY"),
        StringParameter(name="ci_url", label="ci url", size=50,
                        default=constants.CI_SERVER_URL),
        ChoiceStringParameter(
            name="smoke",
            label="Run fast versions of every test",
            choices=["yes", "no"],
            default="yes"),
        ChoiceStringParameter(
            name="big",
            label="Use larger number of VMs",
            choices=["yes", "no"],
            default="yes"),
        ChoiceStringParameter(
            name="backend_ssl",
            label="Backend ssl",
            choices=["no", "yes"],
            default="no"),
        ChoiceStringParameter(
            name="use_snapshots",
            label="Use snapshots",
            choices=["no", "yes"],
            default="no"),
        StringParameter(name="logs_dir", label="Logs dir", size=50, default=os.environ['HOME'] + "/LOGS"),
        ChoiceStringParameter(
            name="no_vm_revert",
            label="No vm revert",
            choices=["no", "yes"],
            default="no"),
        ChoiceStringParameter(
            name="template",
            label="Template",
            choices=['default', 'nogalera', 'twomaxscales'],
            default='default'),
        StringParameter(name="config_to_clone", label="Config to clone", size=50),
    ]
)

SCHEDULERS = [REPOSITORY_SCHEDULER, MANUAL_SCHEDULER]
