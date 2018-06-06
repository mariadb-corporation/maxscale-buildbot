import itertools
from . import build
from . import run_test
from . import run_test_snapshot

MAXSCALE_SERVICES = list(itertools.chain(
    build.SERVICES,
    run_test.SERVICES,
    run_test_snapshot.SERVICES
))
