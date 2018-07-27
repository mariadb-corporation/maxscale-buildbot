from buildbot.data.resultspec import Filter
from buildbot.plugins import reporters, util
from buildbot.reporters import utils
from buildbot.reporters.message import MessageFormatter
from twisted.internet import defer
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
    <h4>Test results:</h4>
    <blockquote>
        <pre>
        {% if build['testResult'] %}
            <p>{{ build['testResult'] }}</p>
        {% else %}
            -
        {% endif %}
        </pre>
    </blockquote>
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
        messageFormatter=ExpandedStepsFormatter(template=template, template_type='html',
                                                wantProperties=True, wantSteps=True,
                                                ctx=dict(statuses=util.Results,
                                                         colors=RESULT_COLOR)),
        sendToInterestedUsers=True,
        subject="[maxscale-buildbot] Buildbot %(result)s in %(title)s on %(builder)s",
        relayhost=config['relayhost'],
        smtpPort=config['smtpPort'],
        useTls=config['useTls'],
        smtpUser=config['smtpUser'],
        smtpPassword=config['smtpPassword'],
    )


class ExpandedStepsFormatter(MessageFormatter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @defer.inlineCallbacks
    def buildAdditionalContext(self, master, ctx):
        """
        Expands steps with results of triggered builds
        :param master: buildmaster for this build
        :param ctx: context of mail template
        :return:
        """
        ctx.update(self.ctx)
        steps = []
        testResults = ''
        for step in ctx['build']['steps']:
            step['triggeredBuilds'] = []
            for url in step['urls']:
                buildRequestId = url['name'].split('#')[-1]
                builds = yield master.data.get(('buildrequests', buildRequestId, 'builds'))
                if builds:
                    build = {'results': builds[0]['results']}
                    buildId = builds[0]['buildid']
                    buildProperties = yield master.data.get(("builds", buildId, 'properties'))
                    build['name'] = buildProperties['virtual_builder_name'][0] or \
                        buildProperties['buildername'][0]
                    build["build_url"] = utils.getURLForBuild(master, builds[0]['builderid'],
                                                              buildId)
                    testResult = yield self.getTestLog(master, buildId)
                    step['triggeredBuilds'].append(build)
                    if testResult:
                        testResults += testResult['content']
            steps.append(step)

        testResult = yield self.getTestLog(master, ctx['build']['buildid'])
        if not testResults and testResult:
            testResults = testResult['content']
        ctx['build']['testResult'] = testResults
        ctx['build']['steps'] = steps

    def getTestLog(self, master, buildId):
        """
        Seeks for 'test_result' step in build and returns its log
        :param master: buildmaster for this build
        :param buildId: id of this build
        :return: stdout of 'test_result' step
        """
        def getStepLog(step):
            if step:
                return master.data.get(('builds', buildId, 'steps',
                                        'test_result', 'logs', 'stdout', 'contents'))

        return master.data.get(('builds', buildId, 'steps'),
                               filters=[Filter("name", "eq", ["test_result"])]).addCallback(getStepLog)
