from . import common

MAIL_TEMPLATE = common.COMPLEX_STEPS_BUILD_TEMPLATE + '''\

    <p><b> -- The Buildbot</b></p>
    '''


SERVICES = [common.create_mail_notifier(MAIL_TEMPLATE, ['build_all'])]
