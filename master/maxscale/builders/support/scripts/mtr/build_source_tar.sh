#!/bin/bash
set -x
export script_dir="$(dirname $(readlink -f $0))"
. ${script_dir}/load_vars.sh

docker login --username jenkins --password ${REGISTRY_PASS} registry.abychko.expert:5000

git checkout $branch

./scripts/run-docker-build.sh \
	--git-branch ${branch} --make-sourcetar \
        --code-tree ${PWD}

mkdir -p ${packages_dir}/${target}/SRC
cp -r target/* ${packages_dir}/${target}/SRC/
cp -r scripts ${packages_dir}/${target}/
#mv -vf *_build.log ${packages_dir}/${target}/target
