TEST_TEMPLATE = u'''\
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