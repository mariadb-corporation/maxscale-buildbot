BOXES = [
    'centos_7_libvirt',
    'centos_6_libvirt',
    'centos_5_libvirt',
    'ubuntu_wily_libvirt',
    'ubuntu_trusty_libvirt',
    'ubuntu_precise_libvirt',
    'ubuntu_xenial_libvirt',
    'ubuntu_xenial_aws',
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
    'debian_stretch_aws',
    'suse_13_libvirt',
    'sles_11_aws',
    'sles_12_aws',
    'sles_12_libvirt',
    'rhel_5_aws',
    'rhel_6_aws',
    'rhel_7_aws',
    'fedora_19_aws',
    'fedora_20_aws',
    'fedora_21_aws',
    'fedora_22_aws',
    'fedora_23_aws'
]

DB_VERSIONS = [
    '10.2',
    '10.3',
    '10.0',
    '10.1',
    '5.5',
    '5.1',
    '5.6',
    '5.7',
    '10.3.6',
    '10.3.7'
]

DEFAULT_CMAKE_FLAGS = ('-DBUILD_TESTS=Y -DCMAKE_BUILD_TYPE=Debug -DFAKE_CODE=Y'
                       '-DBUILD_MMMON=Y -DBUILD_AVRO=Y -DBUILD_CDC=Y')

MAXSCALE_REPOSITORY = 'https://github.com/mariadb-corporation/MaxScale.git'

CI_SERVER_URL = 'http://max-tst-01.mariadb.com/ci-repository/'
