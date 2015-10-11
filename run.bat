@echo off
set /p Test= "Which test to run: "
if /i "%Test%" EQU "1" goto :test1
goto :test2


:test1
echo Running test 1 . . .
fuzz.py test http://127.0.0.1:8080/bodgeit --common-words=myWords.txt --vectors=vectors2.txt --sensitive=sensitive.txt --slow=1000 > output.txt
goto :end

:test2
echo Running test 2 . . .
fuzz.py test http://127.0.0.1/dvwa --common-words=myWords.txt --vectors=vectors2.txt --sensitive=sensitive.txt --slow=2000 > output.txt
goto :end

:end
echo Test complete, see output.txt for report.
pause