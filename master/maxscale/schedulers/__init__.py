import itertools
from . import build
from . import build_and_test
from . import build_and_performance_test
from . import build_and_test_snapshot
from . import build_and_test_on_push
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


MAXSCALE_SCHEDULERS = list(itertools.chain(
    build.SCHEDULERS,
    build_and_test.SCHEDULERS,
    build_and_test_on_push.SCHEDULERS,
    build_and_performance_test.SCHEDULERS,
    run_test.SCHEDULERS,
    run_test_snapshot.SCHEDULERS,
    build_all.SCHEDULERS,
    build_for_release.SCHEDULERS,
    build_and_test_snapshot.SCHEDULERS,
    destroy.SCHEDULERS,
    generate_and_sync_repod.SCHEDULERS,
    run_performance_test.SCHEDULERS,
    build_mdbci.SCHEDULERS,
    publish_release.SCHEDULERS,
    create_full_repo.SCHEDULERS,
    create_full_repo_all.SCHEDULERS,
    build_docker_image.SCHEDULERS,
))
