from . import common


MAIL_TEMPLATE = common.BUILD_SUMMARY_HEADER + u'''\
    <p><b> -- The Buildbot</b></p>
    '''


SERVICES = [common.create_mail_notifier(MAIL_TEMPLATE, ['build'])]
