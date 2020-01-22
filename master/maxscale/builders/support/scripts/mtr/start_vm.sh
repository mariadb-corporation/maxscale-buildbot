#!/bin/bash


script_dir=export script_dir="$(dirname $(readlink -f $0))"


export MDBCI_VM_PATH=/$HOME//vms/
export PATH=$PATH:/$HOME/mdbci/
machine_name=${Image}-${target}-${buildnumber}
echo ${machine_name}


cp ${script_dir}/vm_template.json ${MDBCI_VM_PATH}/${machine_name}.json
mdbci generate --template ${machine_name}.json ${machine_name}
mdbci up ${machine_name}


