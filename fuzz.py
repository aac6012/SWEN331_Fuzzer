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

# Needed for discover:
# - Custom authentication
# - Page discovery: (Link discovery and Page guessing)
# - Input discovery: (Parse URLs, Form Parameters, Cookies)
def discover(args):
    # If auth arg is present, use it for 'get' calls.
    # Create the requests session to use for later 'get' calls.
    session = requests.session()
    # If there is an 'auth' arg, post the session the correct login info for the session
    if 'custom-auth' in args.keys():
        if args['custom-auth'] == 'dvwa':
            payload = {'password': 'password', 'username': 'admin'}
            session.post('http://127.0.0.1/dvwa/login.php', data=payload)

    # Link discovery (via crawling)
    crawled_pages = []
    crawlPages(args['url'], crawled_pages, session)
    print('','-'*50, 'CRAWLED LINKS:', '-'*50, sep='\n')
    for page in crawled_pages:
        print(page)
    print('\n')

    # Page guessing
    guessed_pages = guessPages(args['url'], args['common-words'], session)
    print('-'*50, 'GUESSED LINKS:', '-'*50, sep='\n')
    for page in guessed_pages:
        print(page)
    print('\n')

    # Discover the input on both crawled and discovered pages.
    # Form parameters
    discovered_input = discoverInput(crawled_pages + guessed_pages, session)
    print('-'*50, 'DISCOVERED FORM INPUTS:', '-'*50, sep='\n')
    for key in discovered_input.keys():
        print(key, ':')
        for val in discovered_input[key]:
            print(val)
        print('-'*10)
    print('\n')

    # URL Parameters
    url_parameters = discoverURLParameters(crawled_pages + guessed_pages, session)
    print('-'*50, 'DISCOVERED URL PARAMETERS:', '-'*50, sep='\n')
    for key in url_parameters.keys():
        print(key, ':')
        for val in url_parameters[key]:
            print(val)
        print('-'*10)
    print('\n')

    # Get the cookies from just the base directory
    cookies = discoverCookies(args['url'], session)
    print('-'*50, 'DISCOVERED COOKIES', '-'*50, sep='\n')
    print(cookies)


# This will be a recursive function to discover/process all pages.
def crawlPages(url, visited, session):
    visited.append(url)
    current_links = crawlPagesCurrent(url, session)
    for link in current_links:
        if link not in visited:
            crawlPages(link, visited, session)

# This will parse and return the current url's html file to extract links to other pages.
def crawlPagesCurrent(url, session):
    # instantiate the parser
    parser = MyHTMLParser()

    # clear the found_links and found_input lists before feeding it new text.
    parser.found_links = []
    parser.found_input = []

    # make the request to the url
    r = session.get(url)
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

def guessPages(base_url, filename, session):
    guessed_pages = []
    possible_endings = ['', '.php', '.asp', '.html', '.jsp', '.net']
    # Load the file of common words
    f = open(filename, 'r')
    # Each line is a single word
    for line in f:
        # Loop through possible url endings, guessing each.
        for opt in possible_endings:
            url = base_url + '/' + line.strip('\n') + opt
            r = session.get(url)
            # If the page does not return a 404, then that page was successfully guessed.
            if r.status_code != 404:
                guessed_pages.append(url)

    return guessed_pages


def discoverInput(url_list, session):
    inputs = {}
    for url in url_list:
        inputs[url] = []
        for element in discoverInputCurrent(url, session):
            if element not in inputs[url]:
                inputs[url].append(element)
    return inputs

def discoverInputCurrent(url, session):
    # create the parser
    parser = MyHTMLParser()
    # clear the found_input and found_links list
    parser.found_input = []
    parser.found_links = []

    # make the request to the url
    r = session.get(url)
    # feed the returned html text into the parser
    parser.feed(r.text)
    # get the list of links from the parser object
    inputs = parser.found_input
    return inputs



def discoverURLParameters(url_list, session):
    # Create a dict for the params.  The keys will be the url's and the values will be a list of possible params.
    params = {}
    # Loop through all url's provided in url_list
    for url in url_list:
        # Discover all the current params present from the current page's links.
        discovered = discoverURLParametersCurrent(url, session)

        # Loop through each value in the discovered dict.
        for key in discovered:
            # Add the value to the params dict if it is not already there. If it is already there, don't add it again.
            if key not in params.keys():
                params[key] = discovered[key]

    return params

# This acts similarly to crawlPagesCurrent in that it rips the links first and then returns a dict
# containing the page url as a key and all the discovered parameters as the value(s).
def discoverURLParametersCurrent(url, session):
    # instantiate the parser
    parser = MyHTMLParser()
    # clear the found_input and found_links list
    parser.found_input = []
    parser.found_links = []

    # make the request to the url
    r = session.get(url)
    # feed the returned html text into the parser
    parser.feed(r.text)
    # get the list of links from the parser object
    links = parser.found_links

    urlParams = {}
    # loop through all links to check that each link is properly formed
    for link in links:
        if not link.startswith('http://'):
            link = r.url[:r.url.rfind('/')+1] + link
        # This will find any '?' characters in the link, signifying parameters.
        params_index = link.rfind('?')
        # The base url will be the same regardless of the parameters passed, so eliminate the parameters from the link.
        if params_index != -1 and r.status_code != '404':
            # Split the parameters by '&' symbol.
            params = link[params_index+1:].split('&')
            # Eliminate the assigned value of param to extract param name.
            for x in range(0, len(params)):
                params[x] = params[x][:params[x].rfind('=')]
            link_no_params = link[:params_index]
            if link_no_params not in urlParams.keys():
                urlParams[link_no_params] = params
            else:
                for p in params:
                    if p not in urlParams[link_no_params]:
                        urlParams[link_no_params].append(p)

    return urlParams


# This will discover all the cookies for the url.
# There is no need to loop through any more than one url becuase the cookies are the same throughout the site.
def discoverCookies(url, session):
    r = session.get(url)
    return r.cookies

def fuzz(args):
    pass


if __name__ == '__main__':
    main(sys.argv)