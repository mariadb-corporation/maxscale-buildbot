export packages_dir=${packages_dir:-$HOME/es_packages/}
export REGISTRY_PASS=`cat .config/mdbci/docker-reg`
export Image=${Image:-"rhel-8"}
export BuildType=${BuildType:-"RelWithDebInfo"}
export mtrParam=${mtrParam:-"--mtr-normal-test"}

