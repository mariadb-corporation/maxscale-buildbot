import itertools
from . import build
from . import run_test
from . import download_shell_scripts
from . import destroy
from . import remove_lock
from . import smart_remove_lock
from . import cleanup
from . import build_and_test

MAXSCALE_SCHEDULERS = list(itertools.chain(
    build.SCHEDULERS,
    run_test.SCHEDULERS,
    download_shell_scripts.SCHEDULERS,
    destroy.SCHEDULERS,
    remove_lock.SCHEDULERS,
    smart_remove_lock.SCHEDULERS,
    cleanup.SCHEDULERS,
    build_and_test.SCHEDULERS
))
