"""
This handles the setup stuff for the fuzzer.
"""

import sys
import getopt

def getArgs(passed_args):
    args = {}
    # Get the arguments passed from command line.
    passed_args = passed_args[1:]  # eliminate the running file from args.
    # Exit if there are not enough parameters
    if len(passed_args) < 2:
        print('Not enough parameters: fuzz <mode> <url> <options>')
        sys.exit(0)

    # Get the mode argument.
    args['mode'] = passed_args[0]
    long_options = []
    # If invalid mode, output message and exit.
    if not (args['mode'] == 'discover' or args['mode'] == 'test'):
        print('Not a valid <mode> param.  Must be \'discover\' or \'test\'')
        sys.exit(0)
    # Define the valid options
    elif args['mode'] == 'discover':
        long_options = ['custom-auth=', 'common-words=']
    elif args['mode'] == 'test':
        long_options = ['custom-auth=', 'vectors=', 'sensitive=', 'random=', 'slow=']
    # Get the url argument
    args['url'] = passed_args[1]
    # TODO (maybe): validate url input.
    if not args['url']:
        print('Not a valid url!')
        sys.exit(0)

    # Eliminate the mode and url to leave only options
    passed_args = passed_args[2:]

    # Parse the options, program will terminate if invalid option detected.
    parsed_options = []
    try:
        parsed_options = getopt.getopt(passed_args, '', long_options)
    except getopt.GetoptError as e:
        print('\n', e.msg, sep='')
        print('Valid options for', args['mode'],':')
        for opt in long_options:
            print('\t--', opt[:-1], sep='')
        sys.exit(0)

    # Add the extracted options to the args dict
    for opt in parsed_options[0]:
        if (opt[0][2:] + '=') in long_options:
            args[opt[0][2:]] = opt[1]

    # Check that the required option args exist
    if args['mode'] == 'discover':
        keys = args.keys()
        if 'common-words' not in keys:
            print('Unable to run.\nDiscover requires the \'--common-words\' option to be specified.')
            sys.exit(0)
    elif args['mode'] == 'test':
        keys = args.keys()
        # Check for required args
        if 'vectors' not in keys:
            print('Unable to run.\nTest requires the \'--vectors\' option to be specified.')
            sys.exit(0)
        elif 'sensitive' not in keys:
            print('Unable to run.\nTest requires the \'--sensitive\' option to be specified.')
            sys.exit(0)
        # Set non-required args to default if not specified.
        if 'random' not in keys:
            args['random'] = False
        if 'slow' not in keys:
            args['slow'] = 500

    # Return the constructed args dict.
    return args
