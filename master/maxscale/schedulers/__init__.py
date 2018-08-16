import itertools
from . import build
from . import build_and_test
from . import build_and_test_snapshot
from . import run_test
from . import run_test_snapshot
from . import build_all
from . import build_for_release
from . import destroy
from . import generate_and_sync_repod


MAXSCALE_SCHEDULERS = list(itertools.chain(
    build.SCHEDULERS,
    build_and_test.SCHEDULERS,
    run_test.SCHEDULERS,
    run_test_snapshot.SCHEDULERS,
    build_all.SCHEDULERS,
    build_for_release.SCHEDULERS,
    build_and_test_snapshot.SCHEDULERS,
    destroy.SCHEDULERS,
    generate_and_sync_repod.SCHEDULERS,
))
