from . import common

SERVICES = [common.create_mail_notifier(common.TEST_TEMPLATE, ['build_and_test_snapshot'])]
