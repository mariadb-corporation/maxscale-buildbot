import itertools
from . import build
from . import run_test
from . import download_shell_scripts
from . import destroy

MAXSCALE_SCHEDULERS = list(itertools.chain(
    build.SCHEDULERS,
    run_test.SCHEDULERS,
    download_shell_scripts.SCHEDULERS,
    destroy.SCHEDULERS
))
