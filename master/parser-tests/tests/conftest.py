import pytest


def pytest_addoption(parser):
    parser.addoption("--source", action="append", default=[], help="Test results location")


def pytest_generate_tests(metafunc):
    if 'source' in metafunc.fixturenames:
        metafunc.parametrize("source", metafunc.config.getoption('source'),
                             scope="session")


@pytest.fixture(scope="session")
def sources(request):
    return request.config.getoption('--source')
