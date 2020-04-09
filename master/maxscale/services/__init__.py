import itertools
from . import build
from . import run_test
from . import run_test_snapshot
from . import build_all
from . import build_and_test
from . import build_and_test_parall
from . import build_and_test_shapshot
from . import build_for_release

MAXSCALE_SERVICES = list(itertools.chain(
    build.SERVICES,
    run_test.SERVICES,
    run_test_snapshot.SERVICES,
    build_all.SERVICES,
    build_and_test.SERVICES,
    build_and_test_parall.SERVICES,
    build_and_test_shapshot.SERVICES,
    build_for_release.SERVICES,
))
