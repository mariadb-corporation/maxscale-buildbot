from buildbot.plugins import reporters
from maxscale.config import mailer_config


def create_mail_notifier():
    template_test = u'''\
    <a href="{{ build_url }}">{{ buildername }}</a>
    <h4>Build status: {{ summary }}</h4>
    <p> Worker used: {{ workername }}</p>
    <br>
    <b>Steps results:</b>
    {% for step in build['steps'] %}
    <p> {{ step['name'] }}: {{ step['result'] }}</p>
    {% endfor %}
    <br>

    <h4>Build results:</h4>
    <blockquote>
        <pre>
            {% if 'build_results_content' in build['properties'] %}
                {{ build['properties']['build_results_content'][0] }}
            {% else %}
                -
            {% endif %}
        </pre>
    </blockquote>

    <h4>Coredumps:</h4>
    <blockquote>
        <pre>
            {% if 'coredumps_results_content' in build['properties'] %}
                {{ build['properties']['coredumps_results_content'][0] }}
            {% else %}
                -
            {% endif %}
        </pre>
    </blockquote>

    <a href="{{
            'http://max-tst-01.mariadb.com/LOGS/{}-{}/LOGS/'.format(
                build['properties']['JOB_NAME'][0],
                build['properties']['BUILD_ID'][0]
            )
        }}">
        Logs(ctest logs) for each test
    </a>

    <p><b> -- The Buildbot</b></p>
    '''

    config = mailer_config.mailer_config

    return reporters.MailNotifier(
        fromaddr=config['fromaddr'],
        mode=('failing', 'passing', 'warnings', 'cancelled'),
        extraRecipients=config['extraRecipients'],
        builders=('run_test'),
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
