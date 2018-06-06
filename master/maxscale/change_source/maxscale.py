import re
from buildbot.changes.gitpoller import GitPoller
from maxscale.config import constants
from maxscale.config.branches_list_file import MAXSCALE_BRANCHES_LIST


def check_branch_fn(branch):
    for branch_item in MAXSCALE_BRANCHES_LIST:
        if re.search(branch_item["branch"], branch.split('/')[-1]):
            return True
    return False


def get_test_set_by_branch(branch):
    for branch_item in MAXSCALE_BRANCHES_LIST:
        if re.search(branch_item["branch"], branch):
            return branch_item["test_set"]
    return None


POLLERS = [
    GitPoller(repourl=constants.MAXSCALE_REPOSITORY,
              branches=check_branch_fn, pollinterval=3600, project='maxscale')
]
