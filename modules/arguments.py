import argparse
from argparse import Namespace

args = None


def process_arguments(version_description):
    global args
    parser = argparse.ArgumentParser(description=version_description)
    parser.add_argument('-files', '--f', dest='files', required=True, help='Comma-delimited list of HTML AWR files', default='')
    parser.add_argument('-config', '--c', dest='config', help='Path to configuration file', default='AWR2Excel.toml')
    parser.add_argument('-output', '--o', dest='output', help='Output directory', default='output')
    parser.add_argument('-summary', '--s', dest='summary', help='Generate only summary tabs', action='store_true')

    # If parse fail will show help
    args = parser.parse_args()
    return args


def get_args():
    global args
    return args


def print_arguments():
    global args
    print(f"\nArguments:")
    print(f"\targuments: {args}")
