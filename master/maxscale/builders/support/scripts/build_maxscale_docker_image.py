#!/usr/bin/env python3
# Script is used to build the MaxScale docker image.
# Script is meant to be run from the maxscale-docker repository inside the maxscale folder.
# It uses MDBCI to query the repository configuration to use.


import argparse
import logging
import os
import subprocess
import sys

MDBCI_VM_PATH = os.path.expanduser("~/vms/")


def setupMdbciEnvironment():
    """
    Methods modifies the environment, so the VM managed by the MDBCI will always be in `~/vms/` directory.

    Also adds the `~/mdbci/` to the executable search path. This method should be called before calling mdbci
    """
    os.environ["MDBCI_VM_PATH"] = MDBCI_VM_PATH
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.path.expanduser('~/mdbci')


def parseArguments():
    options = argparse.ArgumentParser(description="MaxScale docker image builder")
    options.add_argument("--product", help="Name of the MDBCI product to query information", default="maxscale_ci")
    options.add_argument("--product-version", help="Version of the MDBCI product to get repository to", required=True)
    options.add_argument("--platform", help="Name of the platform used in the Docker image", default="ubuntu")
    options.add_argument("--platform-version", help="Version of the platform in the Docker image", default="bionic")
    options.add_argument("--name", help="Name of the image to generate", default="mariadb/maxscale-ci")
    options.add_argument("--tag", help="The tag for the image to be generated", required=True)
    options.add_argument("--registry", help="The Docker registry to publish the image to", required=True)
    options.add_argument("--base-image", help="Name of the base image to update", default="ubuntu:bionic")
    return options.parse_args()


def extractRepositoryInformation(product, product_version, platform, platform_version):
    process = subprocess.run(
        ["mdbci", "show", "repository", "--product", product, "--product-version", product_version,
         "--platform", platform, "--platform-version", platform_version, "--silent"],
        stdout=subprocess.PIPE
    )
    print(process.stdout)
    if process.returncode != 0:
        return None
    return process.stdout.strip().decode('utf-8')


def placeRepositoryFile(repository):
    logging.info("Creating repository description")
    repositoryDescription = "deb {}".format(repository)
    repoFile = open("maxscale.list", "w")
    repoFile.write(repositoryDescription)
    repoFile.close()


def buildAndPublishDockerImage(baseImage, name, tag, registry):
    logging.info("Updating the base image '%s'", baseImage)
    subprocess.run(["docker", "image", "pull", baseImage], check=True)
    logging.info("Generating the Docker image")
    cutRegistry = registry.replace('https://', '', 1).strip('/')
    fixedTag = tag.replace(':', '-')
    imageName = "{}/{}:{}".format(cutRegistry, name, fixedTag)
    logging.info("Full image name: %s", imageName)
    logging.info("Removing old version of the Docker image")
    subprocess.run(["docker", "image", "rm", "-f", imageName], check=False)
    logging.info("Creating the new Docker image")
    subprocess.run(["docker", "image", "build", "--force-rm", "-t", imageName, "."], check=True)
    logging.info("Publishing image to registry: %s", registry)
    subprocess.run(["docker", "image", "push", imageName], check=True)
    logging.info("Removing build image from the local Docker cache")
    subprocess.run(["docker", "image", "rm", "-f", imageName], check=False)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the application")
    arguments = parseArguments()
    setupMdbciEnvironment()
    repository = extractRepositoryInformation(arguments.product, arguments.product_version, arguments.platform,
                                              arguments.platform_version)
    if repository is None:
        logging.error("Unable to find repository information")
        sys.exit(1)
    placeRepositoryFile(repository)
    buildAndPublishDockerImage(arguments.base_image, arguments.name, arguments.tag, arguments.registry)


if __name__ == "__main__":
    main()
