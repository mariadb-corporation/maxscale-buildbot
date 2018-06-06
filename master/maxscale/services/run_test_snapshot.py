from buildbot.plugins import reporters
from maxscale.config import mailer_config
from . import common


def create_mail_notifier():
    template_test = common.TEST_TEMPLATE

    config = mailer_config.MAILER_CONFIG

    return reporters.MailNotifier(
        fromaddr=config['fromaddr'],
        mode=('failing', 'passing', 'warnings', 'cancelled'),
        extraRecipients=config['extraRecipients'],
        builders=('run_test_snapshot'),
        messageFormatter=reporters.MessageFormatter(template=template_test, template_type='html',
                                                    wantProperties=True, wantSteps=True),
        sendToInterestedUsers=False,
        relayhost=config['relayhost'],
        smtpPort=config['smtpPort'],
        useTls=config['useTls'],
        smtpUser=config['smtpUser'],
        smtpPassword=config['smtpPassword'],
    )


SERVICES = [create_mail_notifier()]
