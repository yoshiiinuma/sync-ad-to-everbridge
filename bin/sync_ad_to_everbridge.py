"""
Gets AD Group and Syncs with Everbridge Group
"""
import argparse
from os.path import dirname, abspath, exists
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
#pylint: disable=wrong-import-position
from api.sync_runner import SyncRunner

def get_argparser():
    """
    Build Argument Parser
    """
    parser = argparse.ArgumentParser(description="Sync AD Group with Everbridge Group")
    #Get Filename or Location
    parser.add_argument('configfile', help='configuration file path')
    return parser

def main():
    """
    Main Function
    """
    args = get_argparser().parse_args()
    if exists(args.configfile):
        runner = SyncRunner(args.configfile)
        runner.run()
    else:
        print('Config File Not Found: ' + args.configfile)

if __name__ == '__main__':
    main()
