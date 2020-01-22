export packages_dir=${packages_dir:-$HOME/es_packages/}
export Image=${Image:-"rhel-8"}
export REGISTRY_PASS=`cat ${script_dir}/docker-reg`
export BuildType=${BuildType:-"RelWithDebInfo"}
export mtrParam=${mtrParam:-"--mtr-normal-test"}

