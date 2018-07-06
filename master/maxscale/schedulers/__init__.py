import itertools
from . import build
from . import build_and_test
from . import build_and_simple_test
from . import run_test
from . import run_test_snapshot
from . import build_all


MAXSCALE_SCHEDULERS = list(itertools.chain(
    build.SCHEDULERS,
    build_and_test.SCHEDULERS,
    run_test.SCHEDULERS,
    run_test_snapshot.SCHEDULERS,
    build_all.SCHEDULERS,
))
