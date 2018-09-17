import re
from buildbot.data.resultspec import Filter
from buildbot.plugins import reporters, util
from buildbot.reporters import utils
from buildbot.reporters.message import MessageFormatter
from buildbot.reporters.mail import MailNotifier
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
    </br>
    '''


TEST_TEMPLATE = BUILD_SUMMARY_HEADER + '''\

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
    {% if build['results'] == 0 %}
        <a href="{{
                'http://max-tst-01.mariadb.com/LOGS/{}-{}/LOGS/'.format(
                    build['properties']['buildername'][0],
                    build['properties']['buildnumber'][0]
                )
            }}">
            Logs(ctest logs) for each test
        </a>
    {% endif %}
    <p><b> -- The Buildbot</b></p>
    '''

COMPLEX_STEPS_BUILD_TEMPLATE = u'''\

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
            </ul>
        {% endif %}
    </li>
    {% endfor %}
    </ul>
    <br>
    '''

SUBJECT_TEMPLATE = "[maxscale-buildbot] {{ buildername }}-{{ build['properties']['buildnumber'][0] }}" \
                   "-{{ build['properties']['branch'][0] }} ended with {{ statuses[build['results']].upper() }}"

RESULT_COLOR = [
    "#8d4",  # success
    "#fa3",  # warnings
    "#e88",  # failure
    "#ade",  # skipped
    "#c6c",  # exception
    "#ecc",  # retry
    "#ecc",  # cancelled
]


def create_mail_notifier(template, builder_names, **kwargs):
    config = mailer_config.MAILER_CONFIG

    return CustomMailNotifier(
        fromaddr=config['fromaddr'],
        mode=('failing', 'passing', 'warnings', 'cancelled'),
        extraRecipients=config['extraRecipients'],
        builders=builder_names,
        messageFormatter=ExpandedStepsFormatter(template=template, template_type='html',
                                                wantProperties=True, wantSteps=True,
                                                subject=SUBJECT_TEMPLATE,
                                                ctx=dict(statuses=util.Results,
                                                         colors=RESULT_COLOR)),
        sendToInterestedUsers=True,
        relayhost=config['relayhost'],
        smtpPort=config['smtpPort'],
        useTls=config['useTls'],
        smtpUser=config['smtpUser'],
        smtpPassword=config['smtpPassword'],
        **kwargs,
    )


class ExpandedStepsFormatter(MessageFormatter):

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
            # Here we filter only urls that match the path to build request
            buildRequestUrls = [url for url in step['urls']
                                if re.match(r'^https?://.*/#buildrequests/\d+$', url['url'])]
            for url in buildRequestUrls:
                build = yield self.getTriggeredBuild(master, url['name'].split('#')[-1])
                if build:
                    testResult = yield self.getTestLog(master, build['buildId'])
                    if testResult:
                        build['testResult'] = testResult['content']
                        testResults += testResult['content']
                    step['triggeredBuilds'].append(build)
            steps.append(step)

        testResult = yield self.getTestLog(master, ctx['build']['buildid'])
        if not testResults and testResult:
            testResults = testResult['content']
        ctx['build']['testResult'] = testResults
        ctx['build']['steps'] = steps

    def getTriggeredBuild(self, master, buildRequestId):
        """
        Seeks for build by the given build request ID
        :param master: buildmaster for the root build
        :param buildRequestId: ID of the build request that triggered wanted build
        :return: Deferred build object or None
        """
        def getBuildInfo(build):
            if build:
                buildId = build[0]['buildid']
                return master.data.get(("builds", buildId, 'properties')).addCallback(
                    lambda properties: {
                        'buildId': buildId,
                        'name': (properties.get('virtual_builder_name') or
                                 properties.get('buildername'))[0],
                        'build_url': utils.getURLForBuild(master,
                                                          build[0]['builderid'],
                                                          build[0]['number']),
                        'results': build[0]['results'],
                        'properties': properties
                    }
                )

        return master.data.get(('buildrequests', buildRequestId,
                                'builds')).addCallback(getBuildInfo)

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


class CustomMailNotifier(MailNotifier):
    """
    Mail notifier which filters email notification based on the way the build started
    """

    def isMessageNeeded(self, build):
        """
        Disables mail notification if build was triggered from parent build
        applies standard rules otherwise
        :param build:
        :return:
        """
        if build["buildset"].get("parent_buildid") and build["buildset"].get("reason") != "rebuild":
            return False
        else:
            return super().isMessageNeeded(build)
