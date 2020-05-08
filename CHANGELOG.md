
0.9.13 / 2020-05-08
===================


  * lazy chains in funcflow, .map handlers in taskflow, qa decorator allows multiple entrypoints per module, selectable by callable name  

  * pypi upload fixing
  * issue with twine
  * ci settings, readme, pypi publishing
  * setup.py - fixed versioning scheme to avoid conflicts during pypi deployment
  * updated CI with staging deploy, dual license, single-source version with setuptools-scm
  * CI - package deploy to PYPI - WIP
  * fixed issue with mysql test when test server is not avalable in environment  * taskflow - fixed several issues with exception handling  * fixing critical issues for sync amqp, adding tests for sync mysql
  * get rid of sentinel in async loops
  * fixed issue with async loop shutdown, now it depends only on input stream StopIteration and global stop event
  * wip, amqp updates + improvements in India
  * docs updated, code refactoring, adding typecast decorators
  * docs - improved conf and docstrings for funcflow and taskflow, eliminating sphinx warnings
  * docs start, improved doctests for taskflow
  * Merge branch 'amqp_loop'
  * differentiate ci.run_asyn and io.asyn.base.run_asyn
  * amqp transformer sample (amqp->python->amqp), improved amqp decorators
  * async amqp publisher decorator - test passed
  * amqp loop - clean shutdown
  * async loop refactoring
  * async loop refactoring
  * merging todo.txt changes
  * fixed critical error in asyncio loop for amqp entrypoint decorator
  * todo misc
  * amqp entrypoint decorator
  * amqp on_message
  * disable docs, wip
  * docs
  * readme.md, remove py3.8
  * test_funcflow fixed
  * requirements.txt - key dependencies
  * requirements.txt - key dependencies
  * ci
  * gitlab-ci
  * 0.9.7
  * Merge branch 'state_observer'
  * fromtype cleanup and draft note  * cmd entrypoint testes, observer, fromtype helper decorator
  * state_observer, influx reflector, funcflow fixes, entrypoint cli with param to run embedded utils from script directly
  * sync with master
  * cassandra/scylladb feature, improving cli entrypoint to handle mutliple entrypoint by named param, cached qs_params for Driver
  * State observer - draft
  * render_diagram function; fixed issue with funcflow.deep_extend in case with integer keys of dict
  * InfluxDB support
  * json serialization - moving to separate module; setup.py for PyPi - fixed issue with nested packages
  * adding Oracle driver, taskflow - error handling - fix type of arguments
  * adding sync amqp io driver, oracle sync driver
  * apitag: tentative and stable
  * issue in dbi - replace underscore and context manager for cursor in execute statement
  * redis - unix socket - fixing host-path issue
  * funcflow and conf modules - fixing issue with value, key order in callback arguments
  * funcflow: dict support in .map(); conf: expose function to replace env vars in trings or dicts
  * log level decreased for taskflow
  * redis sync driver - fixed
  * taskflow is replacement for chains; funcflow tests coverage, funcflow improved methods extend, copy, weld
  * taskflow - WIP
  * config entrypoints and decorators
  * RedisPopQuery, main io entities from generic availabale directly from io package
  * http - support for streaming (exposing internal feature of requests package)
  * http post - data enciding fixed
  * http client fixed
  * improving error handling in chains - datails, place of exception, add .catch to example
  * drivers - differenc behaviour of cursor (no context manager) for sqlite and mysql
  * fixing App class
  * fixed db_pool example
  * connection uri parsing, values substitution for {} placeholders from environment
  * Merge branch 'refactoring'
  * renaming package sync->syn to be more consistent with asyn
  * refactoruing - all tests passed
  * refactoring queries set, mocks usage, io inheritance model
  * http, tentative decorator, overload decorator (draft)
  * async drivers for amqp and redis; async comsumer and publisher base classes
  * v 0.8 label
  * Database entities refactored for generic, sync, async; tests improved
  * New tests added
  * dev requirements
  * rename helpers testcase
  * fix test flow for sample application
  * test template refactored
  * refactoring: package structure, tests, underscore becomes funcflow
  * Cleaning import
  * fix directory name for package
  * package name fix
  * App class which wraps base behaviour with cli arguments
  * example
  * refactoring to package
  * refactored test suite, fixture db
  * Fixed underscore, db io, pools
  * hotfix: invalid source uri for purchases other than clip (subs, wallet)
  * Merge branch 'faker'
  * easyrec added
  * fakedb feature added
  * faker - WIP
  * Multiple pools auto-discovery
  * Multiple pools option
  * log debug level decreased to info
  * looks functional
  * Cleaned
  * Start