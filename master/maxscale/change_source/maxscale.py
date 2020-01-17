import re
from buildbot.changes.gitpoller import GitPoller
from maxscale.config import constants
from maxscale.config.branches_list_file import MAXSCALE_BRANCHES_LIST
from maxscale.config.branches_list_file import MAXSCALE_PERF_BRANCHES_LIST

def check_branch_fn(branch):
    """
    Checks if branch is in the list of MaxScale branches
    :param branch: Name of the MaxScale branch
    :return: True if branch is found
    """
    for branch_item in MAXSCALE_BRANCHES_LIST:
        if re.search(branch_item["branch"], branch.split('/')[-1]):
            return True
    return False


def check_branch_fn_perf(branch):
    for branch_item in MAXSCALE_PERF_BRANCHES_LIST:
        if re.search(branch_item["branch"], branch.split('/')[-1]):
            return True
    return False


def get_test_set_by_branch(branch):
    """
    Returns test set for a given branch or None if nothing found
    :param branch: Name of the MaxScale branch
    :return: Test set name
    """
    for branch_item in MAXSCALE_BRANCHES_LIST:
        if re.search(branch_item["branch"], branch):
            return branch_item["test_set"]
    return None


POLLERS = [
    GitPoller(repourl=constants.MAXSCALE_REPOSITORY,
              branches=check_branch_fn, pollinterval=600, project='MaxScale')
]
