Running a single test module:

To run a single test module, in this case test_antigravity.py:

$ cd <projectname>/src
$ python -m unittest test.test_antigravity
Just reference the test module the same way you import it.

Running a single test case or test method:

Also you can run a single TestCase or a single test method:

$ python -m unittest test.test_antigravity.GravityTestCase
$ python -m unittest test.test_antigravity.GravityTestCase.test_method
Running all tests:

You can also use test discovery which will discover and run all the tests for you, they must be modules or packages named test*.py (can be changed with the -p, --pattern flag):

$ cd new_project
$ python -m unittest discover
This will run all the test*.py modules inside the test package.

