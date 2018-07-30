from . import common
from . import build_and_test

SERVICES = [common.create_mail_notifier(build_and_test.MAIL_TEMPLATE, ['build_and_test_snapshot'])]
