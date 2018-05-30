import itertools
from . import build
from . import run_test
from . import download_shell_scripts
from . import destroy
from . import remove_lock
from . import smart_remove_lock
from . import cleanup
from . import build_and_test

MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    run_test.BUILDERS,
    download_shell_scripts.BUILDERS,
    destroy.BUILDERS,
    remove_lock.BUILDERS,
    smart_remove_lock.BUILDERS,
    cleanup.BUILDERS,
    build_and_test.BUILDERS
))
