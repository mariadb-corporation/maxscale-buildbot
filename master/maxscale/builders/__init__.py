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
from . import run_performance_test
from . import build_mdbci

MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    build_and_test.BUILDERS,
    run_test.BUILDERS,
    run_test_snapshot.BUILDERS,
    build_all.BUILDERS,
    build_for_release.BUILDERS,
    build_and_test_snapshot.BUILDERS,
    destroy.BUILDERS,
    generate_and_sync_repod.BUILDERS,
    run_performance_test.BUILDERS,
    build_mdbci.BUILDERS,
))
