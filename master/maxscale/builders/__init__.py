import itertools
from . import build, run_test

MAXSCALE_BUILDERS = list(itertools.chain(build.BUILDERS, run_test.BUILDERS))
