import itertools
from . import build
from . import run_test
from . import download_shell_scripts
from . import destroy

MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    run_test.BUILDERS,
    download_shell_scripts.BUILDERS,
    destroy.BUILDERS
))
