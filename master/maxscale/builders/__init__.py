import itertools
from . import build
from . import build_and_test
from . import build_and_performance_test
from . import build_and_test_snapshot
from . import run_test
from . import run_test_snapshot
from . import build_all
from . import build_for_release
from . import destroy
from . import generate_and_sync_repod
from . import run_performance_test
from . import build_mdbci
from . import publish_release
from . import create_full_repo
from . import create_full_repo_all
from . import build_docker_image
from . import build_es_star
from . import build_es_bin
from . import run_mtr
from . import build_and_test_es
from . import build_and_test_es_all


MAXSCALE_BUILDERS = list(itertools.chain(
    build.BUILDERS,
    build_and_test.BUILDERS,
    build_and_performance_test.BUILDERS,
    run_test.BUILDERS,
    run_test_snapshot.BUILDERS,
    build_all.BUILDERS,
    build_for_release.BUILDERS,
    build_and_test_snapshot.BUILDERS,
    destroy.BUILDERS,
    generate_and_sync_repod.BUILDERS,
    run_performance_test.BUILDERS,
    build_mdbci.BUILDERS,
    publish_release.BUILDERS,
    create_full_repo.BUILDERS,
    create_full_repo_all.BUILDERS,
    build_docker_image.BUILDERS,
    build_es_star.BUILDERS,
    build_es_bin.BUILDERS,
    run_mtr.BUILDERS,
    build_and_test_es.BUILDERS,
    build_and_test_es_all.BUILDERS,
))
