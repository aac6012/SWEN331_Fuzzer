# This is the main file for the fuzzer.

import sys
import requests
import getopt

def getArgs(passed_args):
    # Get the arguments passed from command line.
    args = passed_args[1:]  # eliminate the running file from args.
    # Exit if there are not enough parameters
    if len(args) < 2:
        print('Not enough parameters: fuzz <mode> <url> <options>')
        sys.exit(0)

    # Get the mode argument.
    mode = args[0]
    # If invalid mode, output message and exit.
    if not (mode == 'discover' or mode == 'test'):
        print('Not a valid <mode> param.  Must be \'discover\' or \'test\'')
        sys.exit(0)

    # Get the url argument
    url = args[1]
    # TODO (maybe): validate url input.
    if not url:
        print('Not a valid url!')
        sys.exit(0)

    # Eliminate the mode and url to leave only options
    args = args[2:]

    # Define the valid options
    long_options = ['custom-auth=', 'common-words=', 'vectors=', 'sensitive=', 'random=', 'slow=']

    # Parse the options, program will terminate if invalid option detected.
    try:
        parsed_options = getopt.getopt(args, '', long_options)
    except getopt.GetoptError as e:
        print('\nInvalid option!', e.msg, sep='\n')
        sys.exit(0)

    # Print the parsed options list of tuples.
    return [mode, url, parsed_options[0]]


def main(passed_args):
    args = getArgs(passed_args)
    print('Mode: ', args[0])
    print('URL: ', args[1])
    print('Options: ', args[2])


if __name__ == '__main__':
    main(sys.argv)