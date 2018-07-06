import itertools
from . import build
from . import run_test
from . import download_shell_scripts
from . import destroy
from . import remove_lock
from . import smart_remove_lock
from . import cleanup
from . import build_and_test
from . import build_and_simple_test
from . import remove_lock_snapshot
from . import run_test_snapshot
from . import smart_remove_lock_snapshot


MAXSCALE_SCHEDULERS = list(itertools.chain(
    build.SCHEDULERS,
    run_test.SCHEDULERS,
    download_shell_scripts.SCHEDULERS,
    destroy.SCHEDULERS,
    remove_lock.SCHEDULERS,
    smart_remove_lock.SCHEDULERS,
    cleanup.SCHEDULERS,
    build_and_test.SCHEDULERS,
    build_and_simple_test.SCHEDULERS,
    remove_lock_snapshot.SCHEDULERS,
    run_test_snapshot.SCHEDULERS,
    smart_remove_lock_snapshot.SCHEDULERS
))
