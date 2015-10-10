"""
This handles the test part of the fuzzer.
"""

#Test all of the possible vectors.
def test(args):
    print("Testing application...")
    #Parse the values from the vectors file.
    values = parseVectors(args['vectors'])
    css(values['CSS'])
    bfo(values['BFO'])
    fse(values['FSE'])
    int(values['INT'])
    sqp(values['SQP'])
    sqi(values['SQI'])
    ldap(values['LDAP'])
    xpath(values['XPATH'])
    xml(values['XML'])

#Cross-site scripting
def css(values):
    print("Testing cross-site scripting")

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
    vectors = dict(CSS=[], BFO=[], FSE=[], INT=[], SQP=[], SQI=[], LDAP=[], XPATH=[], XML=[])

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
                vectors.get(tag).append( line[0:len(line)-1] )

    return vectors