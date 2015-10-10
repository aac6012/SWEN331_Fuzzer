# This is the main file for the fuzzer.
# @author Austin Cook
# @author Jonathan Correia de Barros

import sys
import discover
import test
import init
import requests

# This is the main method run during execution
def main(passed_args):
    args = init.getArgs(passed_args)

    # If auth arg is present, use it for 'get' calls.
    # Create the requests session to use for later 'get' calls.
    session = requests.session()
    # If there is an 'auth' arg, post the session the correct login info for the session
    if 'custom-auth' in args.keys():
        if args['custom-auth'] == 'dvwa':
            payload = {'password': 'password', 'username': 'admin'}
            response = session.post('http://127.0.0.1/dvwa/login.php', data=payload)
            session.cookies = response.cookies

    #Call the appropriate function using the mode param.
    if args['mode'] == 'discover':
        discovered = discover.discover(args, session)
        outputResults(discovered)

    elif args['mode'] == 'test':
        test.test(args, session)

    else: # This else is somewhat redundant.  Mode input is verified in getArgs.
        print('Not a valid <mode> param.  Must be \'discover\' or \'test\'')
        sys.exit(0)

#Outputs the results returned from discover.
def outputResults(discovered):
    #Output results from discover.
    print('','-'*50, 'CRAWLED LINKS:', '-'*50, sep='\n')
    for page in discovered['crawledPages']:
        print(page)
    print('\n')

    print('-'*50, 'GUESSED LINKS:', '-'*50, sep='\n')
    for page in discovered['guessedPages']:
        print(page)
    print('\n')

    print('-'*50, 'DISCOVERED FORM INPUTS:', '-'*50, sep='\n')
    for key in discovered['formParams'].keys():
        print(key, ':')
        for val in discovered['formParams'][key]:
            print(val['text'])
        print('-'*10)
    print('\n')

    print('-'*50, 'DISCOVERED URL PARAMETERS:', '-'*50, sep='\n')
    for key in discovered['urlParams'].keys():
        print(key, ':')
        for val in discovered['urlParams'][key]:
            print(val)
        print('-'*10)
    print('\n')

    print('-'*50, 'DISCOVERED COOKIES', '-'*50, sep='\n')
    print(discovered['cookies'])

if __name__ == '__main__':
    main(sys.argv)