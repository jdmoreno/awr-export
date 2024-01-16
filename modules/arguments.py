import argparse
from argparse import Namespace

args = None


def process_arguments(version_description):
    global args
    parser = argparse.ArgumentParser(description=version_description)
    parser.add_argument('-files', '-f', required=True, help='Comma-delimited list of HTML AWR files', default='')
    parser.add_argument('-config', '-c', help='Path to configuration file', default='AWR2Excel.ini')
    parser.add_argument('-output', '-o', help='Output directory', default='output')

    # If parse fail will show help
    args = parser.parse_args()
    return args


def get_args():
    global args
    return args
