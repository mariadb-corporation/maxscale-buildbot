from . import common


MAIL_TEMPLATE = u'''\
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


SERVICES = [common.create_mail_notifier(MAIL_TEMPLATE, ('build'))]
