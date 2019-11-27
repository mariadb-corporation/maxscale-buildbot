#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys


def check_local_directory(user_input):
    if not os.path.exists(user_input):
        raise argparse.ArgumentTypeError("The specified local directory '{user_input}' does not exist!".format(
            user_input=user_input))
    if not os.path.isdir(user_input):
        raise argparse.ArgumentTypeError("The specified path '{user_input}' is not a directory!".format(
            user_input=user_input))
    result = os.path.normpath(user_input)
    return result.rstrip('/')


def check_identity_file(user_input):
    if not os.path.exists(user_input):
        raise argparse.ArgumentParser("The specified identity file '{user_input}' does not exist!".format(
            user_input=user_input))
    if not os.path.isfile(user_input):
        raise argparse.ArgumentParser("The specified path '{user_input}' is not a file!".format(
            user_input=user_input))
    return user_input


def check_remote_directory(server, remote_directory, identity_file):
    logging.info("Checking connection to the remote host '{server}'".format(server=server))
    result = subprocess.run(["ssh", "-i", identity_file, server, "echo OK"], stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE)
    if result.returncode != 0:
        logging.error("Unable to connect to the remote host '{server}'".format(server=server))
        logging.error(result.stdout)
        return False

    result = subprocess.run(["ssh", "-i", identity_file, server, "test -d '{remote_directory}'".format(
        remote_directory=remote_directory)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        logging.error("The remote directory '{remote_directory}' does not exist on '{server}'".format(
            remote_directory=remote_directory, server=server))
        logging.error(result.stdout)
        return False
    return True


def setup_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def parse_arguments(args):
    parser = argparse.ArgumentParser(description="Transfer directory from local machine to the remote using rsync")
    parser.add_argument("local_directory", help="Path to the local directory to transfer to remote computer",
                        type=check_local_directory)
    parser.add_argument("server", help="Server identity to connect to supplied with user if necessary")
    parser.add_argument("remote_directory", help="Location on the remote server to put put files")
    parser.add_argument("identity_file", help="SSH identity file location",
                        type=check_identity_file)
    parser.add_argument("--debug", default=False, action="store_true", help="Enable extra debug output")
    arguments = parser.parse_args(args=args)
    return arguments


def transfer_files(local_directory, server, remote_directory, identity_file):
    remote_path = "{server}:{remote_directory}".format(server=server, remote_directory=remote_directory)
    logging.info("Putting local files '{local_directory}' to '{remote_path}'".format(
        local_directory=local_directory, remote_path=remote_path))
    result = subprocess.run(["rsync", "-Pav", "-e", "ssh -i {identity_file}".format(identity_file=identity_file),
                            local_directory, remote_path])
    if result.returncode != 0:
        logging.error("Error during file transfer. See log above for more information")
        return False
    return True


def main(args=None):
    arguments = parse_arguments(args)
    setup_logging(arguments.debug)
    if not check_remote_directory(arguments.server, arguments.remote_directory, arguments.identity_file):
        return
    if not transfer_files(arguments.local_directory, arguments.server, arguments.remote_directory,
                          arguments.identity_file):
        sys.exit(1)


if os.path.samefile(__file__, sys.argv[0]):
    main()
