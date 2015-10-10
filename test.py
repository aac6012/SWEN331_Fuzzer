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
    discovered = discover.discover(args, session)

    xss(vectors['XSS'], discovered, args['slow'])
    #bfo(vectors['BFO'])
    #fse(vectors['FSE'])
    #int(vectors['INT'])
    #sqp(vectors['SQP'])
    #sqi(vectors['SQI'])
    #ldap(vectors['LDAP'])
    #xpath(vectors['XPATH'])
    #xml(vectors['XML'])

#Cross-site scripting
def xss(vector, discovered, slow):
    print("Testing cross-site scripting")

    #Uncomment this line will to cause a 404 error later on.
    #discovered['formParams']['http://127.0.0.1/dvwa/404'] = [{'name': '404'}]

    #Loop through each key in formParams, each key is a url
    for url in discovered['formParams'].keys():
        #Loop through each value in the vector list.
        for value in vector:
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
                print("Slow response time, possible DOS!")
                print("URL: ", url)
                print("Params: ", payload)
                print("Response time: ", response_time)
                print()
            #Check for error codes returned from the response object.
            try:
                response.raise_for_status()
            except exceptions.HTTPError as e:
                print(e)
                print('URL: ', url)
                print('Params: ', payload)



#Buffer overflow
def bfo(values):
    print("Testing Buffer Overflow")

#Format string errors
def fse(values):
    print("Testing format string errors")

#Integer overflow
def int(values):
    print("Testing integer overflow")

#Passive SQL Injection
def sqp(values):
    print("Testing passive SQL injection")

#Active SQL Injection
def sqi(values):
    print("Testing active SQL injection")

#LDAP Injection:
def ldap(values):
    print("Testing LDAP Injection")

#XPATH injection
def xpath(values):
    print("Testing XPATH Injection")

#XML Injection
def xml(values):
    print("Testing XML Injection")


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