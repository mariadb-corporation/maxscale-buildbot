import itertools
from . import build
from . import run_test
from . import run_test_snapshot
from . import build_all

MAXSCALE_SERVICES = list(itertools.chain(
    build.SERVICES,
    run_test.SERVICES,
    run_test_snapshot.SERVICES,
    build_all.SERVICES
))
