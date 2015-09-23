# This is the main file for the fuzzer.

import sys
import requests
import getopt
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    found_links = []
    found_input = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.found_links.append(attrs[0][1])
        if tag == 'input':
            self.found_input.append(self.get_starttag_text())
            pass

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
        print('\nInvalid option!', e.msg, sep='\n')
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


# This is the main method run during execution
def main(passed_args):
    args = getArgs(passed_args)

    if args['mode'] == 'discover':
        discover(args)
    elif args['mode'] == 'fuzz':
        fuzz(args)
    else: # This else is somewhat redundant.  Mode input is verified in getArgs.
        print('Not a valid <mode> param.  Must be \'discover\' or \'test\'')
        sys.exit(0)

def discover(args):
    # Needed for discover:
    # - Custom authentication
    # - Page discovery: (Link discovery and Page guessing)
    crawled_pages = []
    crawlPages(args['url'], crawled_pages)
    print('','-'*50, 'CRAWLED LINKS:', '-'*50, sep='\n')
    for page in crawled_pages:
        print(page)
    print('\n')
    # Page guessing
    guessed_pages = guessPages(args['url'], args['common-words'])
    print('-'*50, 'GUESSED LINKS:', '-'*50, sep='\n')
    for page in guessed_pages:
        print(page)
    print('\n')

    # - Input discovery: (Parse URLs, Form Parameters, Cookies)
    discovered_input = discoverInput(crawled_pages)
    print('-'*50, 'DISCOVERED INPUTS:', '-'*50, sep='\n')
    for key in discovered_input.keys():
        print(key, ':')
        for val in discovered_input[key]:
            print(val)
        print('-'*10)

# This will be a recursive function to discover/process all pages.
def crawlPages(url, visited):
    visited.append(url)
    current_links = crawlPagesCurrent(url)
    for link in current_links:
        if link not in visited:
            crawlPages(link, visited)

# This will parse and return the current url's html file to extract links to other pages.
def crawlPagesCurrent(url):
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
        #Remove the link if it leads to a 404
        if r.status_code == 404:
            links[x] = url

    # add the url returned from the request, in case the url parameter is different.
    links.append(r.url)
    return links

def guessPages(base_url, filename):
    guessed_pages = []
    possible_endings = ['', '.php', '.txt', '.html', '.jsp']
    # Load the file of common words
    f = open(filename, 'r')
    # Each line is a single word
    for line in f:
        # Loop through possible url endings, guessing each.
        for opt in possible_endings:
            url = base_url + '/' + line.strip('\n') + opt
            r = requests.get(url)
            # If the page does not return a 404, then that page was successfully guessed.
            if r.status_code != 404:
                guessed_pages.append(url)

    return guessed_pages






def discoverInput(url_list):
    inputs = {}
    for url in url_list:
        inputs[url] = []
        for element in discoverInputCurrent(url):
            if element not in inputs[url]:
                inputs[url].append(element)
    return inputs

def discoverInputCurrent(url):
    # instantiate the parser
    parser = MyHTMLParser()
    # make the request to the url
    r = requests.get(url)
    # feed the returned html text into the parser
    parser.feed(r.text)
    # get the list of links from the parser object
    inputs = parser.found_input
    return inputs

def fuzz(args):
    pass


if __name__ == '__main__':
    main(sys.argv)