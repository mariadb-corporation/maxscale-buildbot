import itertools
from . import build, run_test, download_shell_scripts

MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    run_test.BUILDERS,
    download_shell_scripts.BUILDERS
))
