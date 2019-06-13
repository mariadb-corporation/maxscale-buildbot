import argparse


def parse_arguments():
    options = argparse.ArgumentParser(description="Docker image builder")
    options.add_argument("repository", help="URL of the repository to pack into the image")
    return options.parse_args()


def main():
    arguments = parse_arguments()


if __name__ == "__main__":
    main()
