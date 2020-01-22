#!/bin/bash
set -x
export script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/load_vars.sh

SOURCETAR=`find ${packages_dir}/${target}/SRC -type f -name mariadb-enterprise-*.tar.gz`
[[ -z "${SOURCETAR}" ]] && exit 1

machine_name=${Image}-${target}-${buildID}

export MDBCI_VM_PATH=/$HOME/vms/
export PATH=$PATH:/$HOME/mdbci/

echo "Get VM info"
export sshuser=`mdbci ssh --command 'whoami' --silent ${machine_name}/build 2> /dev/null | tr -d '\r'`
export IP=`mdbci show network $machine_name/build --silent 2> /dev/null`
export sshkey=`mdbci show keyfile $machine_name/build --silent 2> /dev/null | sed 's/"//g'`
export scpopt="-i $sshkey -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=120 "
export sshopt="$scpopt $sshuser@$IP"

scp ${scpopt} ${SOURCETAR} $sshuser@$IP:~/
ssh ${sshopt} "mkdir MariaDBEnterprise; tar xf mariadb-enterprise-*.tar.gz --strip-components=1 -C MariaDBEnterprise"

scp -r ${scpopt} ${packages_dir}/${target}/scripts $sshuser@$IP:~/MariaDBEnterprise/
ssh ${sshopt} "chmod +x MariaDBEnterprise/scripts/*.sh"

ssh $sshopt "sudo service docker start; sudo docker login --username jenkins --password ${REGISTRY_PASS} registry.abychko.expert:5000; \
        sudo ./MariaDBEnterprise/scripts/run-docker-build.sh --git-branch ${branch} \
	--docker-image ${Image} --build-type ${BuildType}"
	 
mkdir -p ${packages_dir}/${target}/BIN/${Image}/${BuildType}/
scp -r $sshopt:./MariaDBEnterprise/target/* ${packages_dir}/${target}/BIN/${Image}/${BuildType}/

