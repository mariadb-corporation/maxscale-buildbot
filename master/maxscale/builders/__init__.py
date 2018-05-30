import itertools
from . import build
from . import run_test
from . import download_shell_scripts
from . import destroy
from . import remove_lock

MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    run_test.BUILDERS,
    download_shell_scripts.BUILDERS,
    destroy.BUILDERS,
    remove_lock.BUILDERS
))
