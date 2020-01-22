#!/bin/bash
set -x
export script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/load_vars.sh

BINTAR=`find ${packages_dir}/${target}/BIN/${Image}/RelWithDebInfo/ -type f -name '*.tar.gz'`
[[ -z ${BINTAR} ]] && exit 1
echo $BINTAR

cp -r ${packages_dir}/${target}/scripts MariaDBEnterprise/

machine_name=${Image}-${target}-${buildID}

export MDBCI_VM_PATH=/$HOME/vms/
export PATH=$PATH:/$HOME/mdbci/

echo "Get VM info"
export sshuser=`mdbci ssh --command 'whoami' --silent $machine_name/build 2> /dev/null | tr -d '\r'`
export IP=`mdbci show network $machine_name/build --silent 2> /dev/null`
export sshkey=`mdbci show keyfile $machine_name/build --silent 2> /dev/null | sed 's/"//g'`
export scpopt="-i $sshkey -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=120 "
export sshopt="$scpopt $sshuser@$IP"

export mtr=`echo ${mtrParam} | sed "s/-//g"`

ssh $sshopt "mkdir $mtr"

scp ${scpopt} ${BINTAR} $sshuser@$IP:~/$mtr/
ssh ${sshopt} "cd $mtr; mkdir MariaDBEnterprise; tar xf *.tar.gz --strip-components=1 -C MariaDBEnterprise"

scp -r ${scpopt} ${packages_dir}/${target}/scripts $sshuser@$IP:~/$mtr/MariaDBEnterprise/
ssh ${sshopt} "chmod +x $mtr/MariaDBEnterprise/scripts/*.sh; chmod 777 $mtr/MariaDBEnterprise -R"

ssh $sshopt "sudo SCRIPT_ARGS='${mtrParam} --junit-report' DOCKER_NAME=$mtr ./MariaDBEnterprise/scripts/run-docker-build.sh --git-branch ${branch} \
	--docker-image ${Image} --code-tree \${PWD}/${mtr}/MariaDBEnterprise --run-script runtest-es.sh"

mkdir -p ${packages_dir}/${target}/${Image}/XML/${mtrParam}
scp $sshopt:~/MariaDBEnterprise/*.xml MariaDBEnterprise/${packages_dir}/${target}/${Image}/XML/${mtrParam}/

