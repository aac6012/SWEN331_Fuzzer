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


# This is the main method run during execution
def main(passed_args):
    print()
    args = getArgs(passed_args)
    if args[0] == 'discover':
        discover(args[1], args[2:])
    elif args[0] == 'fuzz':
        fuzz(args[1], args[2:])
    else: # This else is somewhat redundant.  Mode input is verified in getArgs.
        print('Not a valid <mode> param.  Must be \'discover\' or \'test\'')
        sys.exit(0)

def discover(url, args):
    # Needed for discover:
    # - Custom authentication
    # - Page discovery: (Link discovery and Page guessing)
    discovered = []
    discoverPages(url, '', discovered)
    print('DISCOVERED LINKS:\n', discovered)
    # - Input discovery: (Parse URLs, Form Parameters, Cookies)
    pass

# This will be a recursive function to discover/process all pages.
def discoverPages(base_url, current_url, visited):
    visited.append(base_url + current_url)
    current_links = discoverPagesCurrent(base_url, current_url)
    for link in current_links:
        if (base_url + link) not in visited:
            discoverPages(base_url, link, visited)

def discoverPagesCurrent(base_url, url):
    r = requests.get(base_url + url)
    lst = r.text.split(base_url)
    lst = lst[1:]
    for x in range(0, len(lst)):
        # Get the element from the list
        element = lst[x]
        # Modify the element to remove tailing text
        element = element[:element.find('\"')]
        if not element.startswith('/'):
            element = '/' + element

        # Store the modified element back into the list
        lst[x] = element
    return lst





def fuzz(url, args):
    pass


if __name__ == '__main__':
    main(sys.argv)