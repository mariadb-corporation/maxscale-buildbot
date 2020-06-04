BOXES = [
    'centos_8_gcp',
    'centos_7_gcp',
    'centos_6_gcp',
    'centos_8_libvirt',
    'centos_7_libvirt',
    'centos_6_libvirt',

    'centos_7_aws',
    'centos_6_aws',

    'rhel_8_gcp',
    'rhel_7_gcp',
    'rhel_6_gcp',
    'rhel_8_libvirt',
    'rhel_6_aws',
    'rhel_7_aws',

    'ubuntu_xenial_gcp',
    'ubuntu_bionic_gcp',
    'ubuntu_focal_gcp',
    'ubuntu_xenial_libvirt',
    'ubuntu_bionic_libvirt',
    'ubuntu_xenial_aws',
    'ubuntu_bionic_aws',

    'suse_15_gcp',
    'suse_13_libvirt',
    'suse_15_libvirt',

    'sles_12_gcp',
    'sles_15_gcp',
    'sles_12_libvirt',
    'sles_12_aws',

    'debian_buster_gcp',
    'debian_stretch_gcp',
    'debian_jessie_libvirt',
    'debian_stretch_libvirt',
    'debian_buster_libvirt',
    'debian_stretch_aws',

    'centos_6_docker',
    'centos_7_docker',
    'centos_6_vbox',
    'fedora_23_aws',
    'docker'
]

BUILD_ALL_BOXES = [
    "centos_7_gcp",
    "centos_6_gcp",
    "centos_8_gcp",
    "ubuntu_xenial_gcp",
    "ubuntu_bionic_gcp",
    'ubuntu_focal_gcp',
    "debian_jessie_aws",
    "debian_stretch_gcp",
    "debian_buster_gcp",
    "sles_12_gcp",
    "suse_15_gcp"
]

DB_VERSIONS = [
    '10.3',
    '10.4',
    '10.2',
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
                       '-DWITH_ASAN=N -DBUILD_GUI=N')

DEFAULT_DAILY_TEST_CMAKE_FLAGS = ('-DBUILD_TESTS=N -DCMAKE_BUILD_TYPE=Debug '
                       '-DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y '
                       '-DWITH_ASAN=N -DBUILD_GUI=N')

DEFAULT_RELEASE_CMAKE_FLAGS = ('-DBUILD_TESTS=N -DBUILD_MMMON=Y '
                               '-DBUILD_CDC=Y -DBUILD_GUI=N')


MAXSCALE_REPOSITORY = 'https://github.com/mariadb-corporation/MaxScale.git'
MAXSCALE_PRODUCT = 'MaxScale'
MDBCI_REPOSITORY = 'https://github.com/mariadb-corporation/mdbci.git'

CI_SERVER_URL = 'https://mdbe-ci-repo.mariadb.net/Maxscale/'

# Define branches for nightly build_all builds
NIGHTLY_SCHEDS = ['2.4', '2.3', 'develop']

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

HOST_USERS = {
    "max-tst-01" : "vagrant",
    "max-gcloud-01" : "timofey_turenko_mariadb_com",
    "max-gcloud-02" : "timofey_turenko_mariadb_com",
    "bb-host" : "timofey_turenko_mariadb_com",
}

HOST_FULL = {
    "max-tst-01" : "max-tst-01.mariadb.com",
    "max-gcloud-01" : "max-gcloud-01",
    "max-gcloud-02" : "max-gcloud-02",
    "bb-host" : "mariadbenterprise-buildbot",
}

UPLOAD_SERVER = "vagrant@max-tst-01.mariadb.com"

UPLOAD_SERVERS = {
    "max-tst-01" : "timofey_turenko_mariadb_com@35.228.225.110",
    "max-gcloud-01" : "timofey_turenko_mariadb_com@10.166.0.24",
    "max-gcloud-02" : "timofey_turenko_mariadb_com@10.166.0.24",
    "bb-host" : "timofey_turenko_mariadb_com@10.166.0.24",
}

UPLOAD_PATH = "/srv/repository/Maxscale"
