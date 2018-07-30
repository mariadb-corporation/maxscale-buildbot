from . import common

MAIL_TEMPLATE = common.COMPLEX_STEPS_BUILD_TEMPLATE + '''\

    <h4>Test results:</h4>
    <ol>
    {% for step in build['steps'] %}
        {% for test in step['triggeredBuilds'] %}
            {% if test['testResult'] %}
                <li><p>Result of {{ test['properties']['buildername'][0] }}</p>
                <blockquote>
                    <p>{{ test['testResult'] }}</p>
                </blockquote>
                {% if build['results'] == 0 %}
                    <a href="{{
                        'http://max-tst-01.mariadb.com/LOGS/{}-{}/LOGS/'.format(
                            test['properties']['buildername'][0],
                            test['properties']['buildnumber'][0]
                        )
                    }}">Logs(ctest logs) for each test</a>
                {% endif %}
                <li>
            {% endif %}
        {% endfor %}
    {% endfor %}
    </ol>
    <p><b> -- The Buildbot</b></p>
    '''

SERVICES = [common.create_mail_notifier(common.TEST_TEMPLATE, ['build_and_test'])]
