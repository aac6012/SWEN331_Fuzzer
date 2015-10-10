# This is the main file for the fuzzer.
# @author Austin Cook
# @author Jonathan Correia de Barros

import sys
import discover
import test
import init

# This is the main method run during execution
def main(passed_args):
    args = init.getArgs(passed_args)

    if args['mode'] == 'discover':
        discover.discover(args)
    elif args['mode'] == 'fuzz':
        test.test(args)
    else: # This else is somewhat redundant.  Mode input is verified in getArgs.
        print('Not a valid <mode> param.  Must be \'discover\' or \'test\'')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv)