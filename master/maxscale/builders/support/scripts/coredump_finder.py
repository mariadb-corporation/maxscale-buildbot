#!/usr/bin/env python3

import argparse
import os
import sys


def main():
    args = parseArguments()
    coreDumps = findCoreDumps(args.directory, args.remote_prefix)
    storeCoreDumps(coreDumps, args.output_file)


def parseArguments():
    parser = argparse.ArgumentParser(description="Core dump finder")
    parser.add_argument("--directory", help="location where to find the core dumps", required=True)
    parser.add_argument("--remote-prefix", help="prefix of the remote server for the core dumps",
                        required=True)
    parser.add_argument("--output-file", help="location of the output file to put data", required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("Directory {} does not exist, exiting.".format(args.directory))
        sys.exit(1)

    return args


def findCoreDumps(directory, prefix):
    paths = []
    if prefix.endswith("/"):
        fixedPrefix = prefix
    else:
        fixedPrefix = "{}/".format(prefix)
    for dirPath, dirNames, fileNames in os.walk(directory):
        for fileName in fileNames:
            if "core" in fileName:
                paths.append(os.path.join(dirPath.replace(directory, fixedPrefix), fileName))
    return paths


def storeCoreDumps(coreDumps, fileName):
    with open(fileName, "w") as file:
        file.write("COREDUMPS \\\n")

        if len(coreDumps) == 0:
            file.write("Coredumps were not found")
        else:
            for dump in coreDumps:
                file.write("{} \\\n".format(dump))


if os.path.samefile(__file__, sys.argv[0]):
    main()

