#!/usr/bin/env python3
import argparse
import json
import os
import subprocess


def main():
    arguments = parse_arguments()
    os.chdir(arguments.directory)
    worker_definitions = generate_workers(arguments.hostname, arguments.amount)
    create_workers(worker_definitions, arguments.master)
    write_json_file(worker_definitions)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create workers and generate the workers definition file')
    parser.add_argument('hostname', help='Name of the host to put into the configuration')
    parser.add_argument('amount', type=int, help='Number of workers to generate')
    parser.add_argument('master', help='Location of the BuildBot master to connect to')
    parser.add_argument('--directory', default='.', help='The location of workers to manage')
    return parser.parse_args()


def generate_workers(hostname, amount):
    workers = []
    for worker_number in range(1, amount + 1):
        password = subprocess.run(['openssl', 'rand', '-hex', '32'], stdout=subprocess.PIPE)\
            .stdout.strip().decode('utf-8')
        workers.append({
            "host": hostname,
            "name": "{}-{:02d}".format(hostname, worker_number),
            "password": password
        })
    return workers


def create_workers(worker_definitions, master):
    for definition in worker_definitions:
        subprocess.run(['buildbot-worker', 'create-worker', definition['name'], master, definition['name'],
                        definition['password']], check=True)


def write_json_file(worker_definitions):
    with open('workers.json', 'w') as outfile:
        json.dump(worker_definitions, outfile, indent=2)


if __name__ == "__main__":
    main()

