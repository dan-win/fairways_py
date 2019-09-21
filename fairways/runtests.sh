#!/bin/bash

this_program="$0"
dirname="`dirname $this_program`"
readlink="`readlink -e $dirname`"

if [ -z "$1" ]; then 
    echo "Runnign all available tests"
    python -m unittest discover -s "$readlink"/test -v
else
    # python3 -m unittest test_module
    echo "Testing $1"
    test_module=$1
    PYTHONPATH="$dirname:$PYTHONPATH"
    echo "---------------->$PYTHONPATH"
    # python3 -m unittest test/$test_module.py
    # python -m unittest discover -s "$readlink"/test -v

    python -m unittest discover -s "$readlink"/test -p "$test_module"  -v

fi

