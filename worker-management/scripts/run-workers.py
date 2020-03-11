#!/usr/bin/env python3
import argparse
import json
import os
import subprocess


def main():
    arguments = parse_arguments()
    os.chdir(arguments.directory)
    start_workers(arguments.hostname, arguments.amount)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create workers and generate the workers definition file')
    parser.add_argument('hostname', help='Name of the host to put into the configuration')
    parser.add_argument('amount', type=int, help='Number of workers to generate')
    parser.add_argument('--directory', default='.', help='The location of workers to manage')
    return parser.parse_args()


def start_workers(hostname, amount):
    for worker_number in range(1, amount + 1):
        name =  "{}-{:02d}".format(hostname, worker_number)
        subprocess.run(['pipenv run buildbot-worker', 'start', name], check=True)
    return 0


if __name__ == "__main__":
    main()

