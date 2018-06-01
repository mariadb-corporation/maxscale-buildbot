from buildbot.plugins import reporters
from maxscale.config import mailer_config


def create_mail_notifier():
    template_build = u'''\
    <a href="{{ build_url }}">{{ buildername }}</a>
    <h4>Build status: {{ summary }}</h4>
    <p> Worker used: {{ workername }}</p>
    <br>
    <b>Steps' results:</b>
    {% for step in build['steps'] %}
    <p> {{ step['name'] }}: {{ step['result'] }}</p>
    {% endfor %}
    <br>
    <p><b> -- The Buildbot</b></p>
    '''

    config = mailer_config.MAILER_CONFIG

    return reporters.MailNotifier(
        fromaddr=config['fromaddr'],
        mode=('failing', 'passing', 'warnings', 'cancelled'),
        extraRecipients=config['extraRecipients'],
        builders=('build'),
        messageFormatter=reporters.MessageFormatter(template=template_build, template_type='html',
                                                    wantProperties=True, wantSteps=True),
        sendToInterestedUsers=False,
        relayhost=config['relayhost'],
        smtpPort=config['smtpPort'],
        useTls=config['useTls'],
        smtpUser=config['smtpUser'],
        smtpPassword=config['smtpPassword']
    )


SERVICES = [create_mail_notifier()]
