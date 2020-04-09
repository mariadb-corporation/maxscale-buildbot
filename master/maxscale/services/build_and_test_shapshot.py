from . import common

SERVICES = [common.create_mail_notifier(common.COMPLEX_TEST_RESULTS_TEMPLATE, ['build_and_test_snapshot'])]
