Fuzzer project for SWEN331 - Engineering Secure Software
Developed by Austin Cook and Jonathan Correia de Barros

Requirements:
- Python >= 3.3
- Python 'requests' package

Setup:
- If 'requests' is not present, you can install it via pip with 'pip install requests'.  This will download the most up-to-date package.
  If pip is not installed, please visit http://www.python-requests.org/en/latest/user/install/#get-the-code for instructions on manual installation.

To run:
1. Open up a command prompt.
2. Navigate to the directory with 'fuzz.py'
3. Run the program using the following format: 'fuzz <mode> <url> <options>'. See below for valid arguments.
4. The program output may be long.  To send the output to a file, add the following to the end of the command line run statment: ' > output.txt'

Valid arguments:
- <mode>: 'discover' or 'test' (Do not enter quotes into the command line statement)
- <url>: Can be any valid url beginning with 'http://'
- <options>: The options are as follows for each mode:
    discover:
        --custom-auth (optional):   Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa).
        --common-words (REQUIRED):  Newline-delimited file of common words to be used in page guessing and input guessing.
    test:
	--common-words (REQUIRED):  The 'test' mode is dependent on the 'discover' mode, so this is a required parameter for test as well.
        --custom-auth (optional):   Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa).
        --vectors (REQUIRED):       Newline-delimited file of common exploits to vulnerabilities.
        --sensitive (REQUIRED):     Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response.
        --random (optional):        When off, try each input to each page systematically.  When on, choose a random page, then a random input field and test all vectors. Default: false.
        --slow (optional):          Number of milliseconds considered when a response is considered "slow". Default is 500 milliseconds.

Example statement:
'fuzz test http://127.0.0.1/dvwa --common-words=myWords.txt --sensitive=sensitive.txt --vectors=vectors.txt --slow=1500'