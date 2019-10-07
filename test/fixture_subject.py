"""
Sample with QueriesSet and QA entrypoint.
Used for test_fixture_template.py
"""

from fairways.io.generic import (QueriesSet, SqlQuery)
from fairways import decorators
from fairways.decorators import entities

@decorators.connection.define()
class TestDb(QueriesSet):
    QUERY1 = SqlQuery(
        "select * from t1",
        "DB_CONN",
        lambda x: x
    )

@decorators.use.connection('dba')
def some_task(ctx, dba=None, unused_arg=None):
    return dba.QUERY1.get_records()

@decorators.entrypoint.qa()
def runner(ctx, middleware=None):
    return some_task(ctx)

