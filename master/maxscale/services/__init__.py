import itertools
from . import build, run_test

MAXSCALE_SERVICES = list(itertools.chain(build.SERVICES, run_test.SERVICES))
