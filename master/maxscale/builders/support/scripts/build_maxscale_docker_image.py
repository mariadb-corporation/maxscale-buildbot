#!/usr/bin/env python3
# Script is used to build the MaxScale docker image.
# Script is meant to be run from the maxscale-docker repository inside the maxscale folder.


import argparse
import logging
import subprocess


def parseArguments():
    options = argparse.ArgumentParser(description="MaxScale docker image builder")
    options.add_argument("--repository", help="URL of the repository to pack into the image", required=True)
    options.add_argument("--name", help="Name of the image to generate", default="mariadb/maxscale-ci")
    options.add_argument("--tag", help="The tag for the image to be generated", required=True)
    options.add_argument("--registry", help="The Docker registry to publish the image to", required=True)
    return options.parse_args()


def placeRepositoryFile(repository):
    logging.info("Creating repository description")
    repositoryDescription = "deb {} bionic main".format(repository)
    logging.info("Repository description: %s", repositoryDescription)
    repoFile = open("maxscale.list", "w")
    repoFile.write(repositoryDescription)
    repoFile.close()


def buildAndPublishDockerImage(name, tag, registry):
    logging.info("Generating the Docker image")
    cutRegistry = registry.replace('https://', '', 1).strip('/')
    fixedTag = tag.replace(':', '-')
    imageName = "{}/{}:{}".format(cutRegistry, name, fixedTag)
    logging.info("Full image name: %s", imageName)
    subprocess.run(["docker", "image", "build", "-t", imageName, "."], check=True)
    logging.info("Publishing image to registry: %s", registry)
    subprocess.run(["docker", "image", "push", imageName], check=True)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the application")
    arguments = parseArguments()
    placeRepositoryFile(arguments.repository)
    buildAndPublishDockerImage(arguments.name, arguments.tag, arguments.registry)


if __name__ == "__main__":
    main()
