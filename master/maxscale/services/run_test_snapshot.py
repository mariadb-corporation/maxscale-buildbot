from . import common
from maxscale.schedulers.run_test_snapshot import MANUAL_SCHEDULER

SERVICES = [common.create_mail_notifier(common.TEST_TEMPLATE, ['run_test_snapshot'],
                                        schedulers=[MANUAL_SCHEDULER.name])]
