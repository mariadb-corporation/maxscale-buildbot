from buildbot.plugins import reporters, util
from maxscale.config import mailer_config


BUILD_SUMMARY_HEADER = u'''\

    <a href="{{ build_url }}">{{ buildername }}</a>
    <h4>Build status: {{ summary }}</h4>
    <p> Worker used: {{ workername }}</p>
    <br>
    <b>Steps results:</b>
    <ul>
    {% for step in build['steps'] %}
    <li> {{ step['name'] }}: <b style='color:{{colors[step['results']]}}'>{{ statuses[step['results']]}}</b></li>
    {% endfor %}
    </ul>
    <br>
    '''


TEST_TEMPLATE = BUILD_SUMMARY_HEADER + '''\

    <a href="{{
            'http://max-tst-01.mariadb.com/LOGS/{}-{}/LOGS/'.format(
                build['properties']['buildername'][0],
                build['properties']['buildnumber'][0]
            )
        }}">
        Logs(ctest logs) for each test
    </a>

    <p><b> -- The Buildbot</b></p>
    '''


RESULT_COLOR = [
    "#8d4",  # success
    "#fa3",  # warnings
    "#e88",  # failure
    "#ade",  # skipped
    "#c6c",  # exception
    "#ecc",  # retry
    "#ecc",  # cancelled
]


def create_mail_notifier(template, builder_names):
    config = mailer_config.MAILER_CONFIG

    return reporters.MailNotifier(
        fromaddr=config['fromaddr'],
        mode=('failing', 'passing', 'warnings', 'cancelled'),
        extraRecipients=config['extraRecipients'],
        builders=builder_names,
        messageFormatter=reporters.MessageFormatter(template=template, template_type='html',
                                                    wantProperties=True, wantSteps=True,
                                                    ctx=dict(statuses=util.Results,
                                                             colors=RESULT_COLOR)),
        sendToInterestedUsers=True,
        relayhost=config['relayhost'],
        smtpPort=config['smtpPort'],
        useTls=config['useTls'],
        smtpUser=config['smtpUser'],
        smtpPassword=config['smtpPassword'],
    )
