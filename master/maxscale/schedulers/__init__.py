import itertools
from . import build
from . import run_test

MAXSCALE_SCHEDULERS = list(itertools.chain(build.SCHEDULERS,
                                           run_test.SCHEDULERS))
