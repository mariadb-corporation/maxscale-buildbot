from . import common

SERVICES = [common.create_mail_notifier(common.TEST_TEMPLATE, ['run_test'])]
