from . import common


MAIL_TEMPLATE = u'''\

    <a href="{{ build_url }}">{{ buildername }}</a>
    <h4>Build status: {{ summary }}</h4>
    <p> Worker used: {{ workername }}</p>
    <br>
    <b>Steps results:</b>
    <ul>
    {% for step in build['steps'] %}
    <li>
        {{ step['name'] }}: <b style='color:{{colors[step['results']]}}'>{{ statuses[step['results']]}}</b>
        {% if step['triggeredBuilds'] %}
            <ul>
            {% for triggeredBuild in step['triggeredBuilds'] %}
                <li>
                    <a href="{{ triggeredBuild['build_url'] }}">{{ triggeredBuild['name'] }}</a>:
                    <b style='color:{{colors[triggeredBuild['results']]}}'>{{ statuses[triggeredBuild['results']]}}</b>
                </li>
            {% endfor %}
            <ul>
        {% endif %}
    </li>
    {% endfor %}
    </ul>
    <br>
    <p><b> -- The Buildbot</b></p>
    '''


SERVICES = [common.create_mail_notifier(MAIL_TEMPLATE, ['build_all'])]
