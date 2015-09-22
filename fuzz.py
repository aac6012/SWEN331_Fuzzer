# This is the main file for the fuzzer.

import sys
import requests
import getopt
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    found_links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.found_links.append(attrs[0][1])

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
    print('\n----------------------------------------')
    args = getArgs(passed_args)
    if args[0] == 'discover':
        # args[1] contains the base url.
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
    discoverPages(url, discovered)
    print('DISCOVERED LINKS:\n', discovered)
    # - Input discovery: (Parse URLs, Form Parameters, Cookies)
    pass

# This will be a recursive function to discover/process all pages.
def discoverPages(url, visited):
    visited.append(url)
    current_links = discoverPagesCurrent(url)
    for link in current_links:
        if link not in visited:
            PARSER_LIST = []
            discoverPages(link, visited)

# This will parse and return the current url's html file to extract links to other pages.
def discoverPagesCurrent(url):
    # instantiate the parser
    parser = MyHTMLParser()
    # make the request to the url
    r = requests.get(url)
    # feed the returned html text into the parser
    parser.feed(r.text)
    # get the list of links from the parser object
    links = parser.found_links
    # loop through all links to check that each link is properly formed
    for x in range(0, len(links)):
        if not links[x].startswith('http://'):
            links[x] = r.url[:r.url.rfind('/')+1] + links[x]
        # This will find any '?' characters in the link, signifying parameters.
        params_index = links[x].rfind('?')
        # The base url will be the same regardless of the parameters passed, so eliminate the parameters from the link.
        if params_index != -1:
            links[x] = links[x][:params_index]

    # add the url returned from the request, in case the url parameter is different.
    links.append(r.url)
    return links



def fuzz(url, args):
    pass


if __name__ == '__main__':
    main(sys.argv)