import itertools
from . import build
from . import build_and_test
from . import build_and_simple_test
from . import run_test
from . import run_test_snapshot
from . import build_all

MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    build_and_test.BUILDERS,
    run_test.BUILDERS,
    run_test_snapshot.BUILDERS,
    build_all.BUILDERS,
))
