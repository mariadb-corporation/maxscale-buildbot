BOXES = [
    'centos_7_libvirt',
    'centos_6_libvirt',
    'centos_5_libvirt',
    'ubuntu_wily_libvirt',
    'ubuntu_trusty_libvirt',
    'ubuntu_precise_libvirt',
    'ubuntu_xenial_libvirt',
    'ubuntu_bionic_libvirt',
    'ubuntu_xenial_aws',
    'ubuntu_bionic_aws',
    'ubuntu_wily_aws',
    'ubuntu_trusty_aws',
    'ubuntu_precise_aws',
    'ubuntu_yakkety_aws',
    'ubuntu_trusty_docker',
    'ubuntu_precise_vbox',
    'ubuntu_trusty_vbox',
    'centos_7_aws',
    'centos_6_aws',
    'centos_6_docker',
    'centos_7_docker',
    'centos_5_vbox',
    'centos_6_vbox',
    'debian_wheezy_libvirt',
    'debian_jessie_libvirt',
    'debian_stretch_libvirt',
    'debian_buster_libvirt',
    'debian_stretch_aws',
    'suse_13_libvirt',
    'suse_15_libvirt',
    'sles_11_aws',
    'sles_12_aws',
    'sles_12_libvirt',
    'rhel_5_aws',
    'rhel_6_aws',
    'rhel_7_aws',
    'rhel_8_libvirt',
    'fedora_19_aws',
    'fedora_20_aws',
    'fedora_21_aws',
    'fedora_22_aws',
    'fedora_23_aws',
    'docker'
]

BUILD_ALL_BOXES = [
    "centos_7_libvirt",
    "centos_6_libvirt",
    "rhel_8_libvirt",
    "ubuntu_trusty_libvirt",
    "ubuntu_xenial_libvirt",
    "ubuntu_bionic_libvirt",
    "debian_jessie_libvirt",
    "debian_stretch_libvirt",
    "debian_buster_libvirt",
    "sles_12_aws",
    "suse_15_libvirt"
]

DB_VERSIONS = [
    '10.3',
    '10.2',
    '10.4',
    '10.1',
    '10.0',
    '5.5',
    '5.1',
    '5.6',
    '5.7',
    '10.3.6',
    '10.3.7',
    '10.3.8',
    '10.3.9',
    '10.3.10'
]

DEFAULT_CMAKE_FLAGS = ('-DBUILD_TESTS=Y -DCMAKE_BUILD_TYPE=Debug '
                       '-DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y '
                       '-DWITH_ASAN=N')

DEFAULT_DAILY_TEST_CMAKE_FLAGS = ('-DBUILD_TESTS=N -DCMAKE_BUILD_TYPE=Debug '
                       '-DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y '
                       '-DWITH_ASAN=N')

DEFAULT_RELEASE_CMAKE_FLAGS = ('-DBUILD_TESTS=N -DBUILD_MMMON=Y '
                               '-DBUILD_CDC=Y')


MAXSCALE_REPOSITORY = 'git@github.com:mariadb-corporation/MaxScale-private.git'
MDBCI_REPOSITORY = 'https://github.com/mariadb-corporation/mdbci.git'

CI_SERVER_URL = 'http://max-tst-01.mariadb.com/ci-repository/'

# Define branches for nightly build_all builds
NIGHTLY_SCHEDS = ['2.4', '2.3', '2.2', 'develop']

NIGHTLY_MAIL_LIST = ['markus.makela@mariadb.com', 'johan.wikman@mariadb.com', 'esa.korhonen@mariadb.com', 'niclas.antti@mariadb.com']

# Define dictionary with maxscale repositories
MAXSCALE_CODEBASE = {
    "": {
        "branch": "develop",
        "revision": "",
        "repository": MAXSCALE_REPOSITORY
    },
}

MDBCI_CODEBASE = {
    "": {
        "branch": "integration",
        "revision": "",
        "repository": MDBCI_REPOSITORY
    },
}

PERF_CNF_TEMPLATES = [
    'base.cnf.erb',
]

PERF_PORTS = [
    '4006',
    '4008'
]

# Definitions for the Docker product creation
MAXSCALE_CI_DOCKER_PRODUCT_NAME = 'mariadb/maxscale-ci'

DOCKER_REGISTRY = 'https://maxscale-docker-registry.mariadb.net:5000'

MAXSCALE_DOCKER_REPOSITORY = 'https://github.com/mariadb-corporation/maxscale-docker'

MAXSCALE_DOCKER_CODEBASE = {
    "": {
        "branch": "master",
        "revision": "",
        "repository": MAXSCALE_DOCKER_REPOSITORY
    },
}
