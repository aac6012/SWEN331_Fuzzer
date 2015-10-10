"""
This handles the test part of the fuzzer.
"""
import discover
import requests
import time
import requests.exceptions as exceptions

#Test all of the possible vectors.
def test(args, session):

    #Parse the values from the vectors file.
    vectors = parseVectors(args['vectors'])
    #Get the dictionary return from running discover.
    discovered = discover.discover(args, session)
    #Run the tests using the discovered information, list of vectors, and slow parameter.
    run_tests(vectors, discovered, args['slow'])

    print('-'*50, 'Testing completed', '-'*50, sep='\n')

#Test the files
def run_tests(vectors, discovered, slow):

    #Uncomment this line/lines to cause a 404 error later on.
    #discovered['formParams']['http://127.0.0.1/dvwa/404'] = [{'name': '404'}]
    #discovered['urlParams']['http://127.0.0.1:8080/bodgeit/404/'] = ['test']

    print('-'*50)
    print('Testing form parameters.')
    print('-'*50)
    #Loop through each vectors category
    for key in vectors.keys():

        #Loop through each key in formParams, each key is a url
        for url in discovered['formParams'].keys():
            #Loop through each value in the vector list.
            for value in vectors[key]:
                #Construct payload to pass in request
                payload = {}
                for param in discovered['formParams'][url]:
                    payload[param.get('name')] = value
                #Get the start time for the request.
                start_time = time.time()
                #Make the POST request to the url using the build payload.
                response = requests.post(url, data=payload)
                response.content
                #Calculate the response time, using the current and start time.
                response_time = (time.time() - start_time)
                response_time = response_time * 1000

                #Check for possible Denial of Service error from slow response.
                if response_time > slow:
                    print('Slow response time, possible DOS!')
                    print('Vector type: ', key)
                    print('URL: ', url)
                    print('Params: ', payload)
                    print('Response time: ', response_time)
                    print('-----') # Add a line for readability

                #Check for error codes returned from the response object.
                try:
                    response.raise_for_status()
                except exceptions.HTTPError as e:
                    print(e)
                    print('URL: ', url)
                    print('Params: ', payload)
                    print('Vector type: ', key)
                    print('-----') # Add a line for readability


    print('-'*50)
    print('Testing URL Parameters...')
    print('-'*50)
    for key in vectors.keys():

        #Loop through each key in formParams, each key is a url
        for url in discovered['urlParams']:
            #Loop through each value in the vector
            for value in vectors[key]:
                # Create the params to pass in through the request.
                params = {}
                # Build the params
                for param in discovered['urlParams'][url]:
                    params[param] = value

                #Get the start time for the request.
                start_time = time.time()
                #Make the GET request to the url using the built url params.
                response = requests.get(url, params=params)
                response.content
                #Calculate the response time, using the current and start time.
                response_time = (time.time() - start_time)
                response_time = response_time * 1000

                #Check for possible Denial of Service error from slow response.
                if response_time > slow:
                    print('Slow response time, possible DOS!')
                    print('Vector type: ', key)
                    print('URL: ', url)
                    print('Params: ', params)
                    print('Response time: ', response_time)
                    print('-----') # Add a line for readability

                #Check for error codes returned from the response object.
                try:
                    response.raise_for_status()
                except exceptions.HTTPError as e:
                    print(e)
                    print('Params: ', params)
                    print('Vector type: ', key)
                    print('-----') # Add a line for readability




#Parse the vectors file into a dictionary of lists.
def parseVectors(file):
    #Create the dictionary of values to return
    vectors = dict(XSS=[], BFO=[], FSE=[], INT=[], SQP=[], SQI=[], LDAP=[], XPATH=[], XML=[])

    #Create the tag variable to use for parsing.
    tag = 'nothing'

    #Loop through every line in the file, adding the values to the appropriate list in the vector dictionary.
    for line in open(file):
        #Update the tag, if necessary.
        if line.startswith('--END ' + tag + '--'):
            tag = 'nothing'
        elif line.startswith('--'):
            #Remove the dashes
            tag = line.replace('--','')
            #Remove the new line character
            tag = tag[0:len(tag)-1]
        else:
            #If the tag didn't change, add the current value to the appropriate list.
            if tag in vectors.keys():
                #Add the current line to the list, removing the next line character.
                vectors.get(tag).append( line[0:len(line)-1] )

    return vectors