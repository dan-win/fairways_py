#!/bin/bash
set -eu
# Module which contains tests (without package name):
module=$1
# Name of class which contains tests:
class=$2
# Name of method to run:
method=$3
# E.g.:
# python -m test.test_taskflow TaskFlowTestCase.test_catch_on_any_error
python -m test.$module $class.$method
