#!/bin/bash

this_program="$0"
dirname="`dirname $this_program`"
readlink="`readlink -e $dirname`"

python -m unittest discover -s "$readlink"/test -v
