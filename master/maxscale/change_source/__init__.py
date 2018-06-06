import itertools
from . import maxscale


MAXSCALE_POLLERS = list(itertools.chain(
    maxscale.POLLERS
))
