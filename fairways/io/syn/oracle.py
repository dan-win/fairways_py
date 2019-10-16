# -*- coding: utf-8 -*-

import cx_Oracle
import re
from collections import namedtuple

from .base import (SynDataDriver)

import logging
log = logging.getLogger(__name__)

# RE_CONN_TEMPLATE = re.compile(r"(?:(?P<user>[^/]*)/(?P<password>[^@]*)@//)?(?P<host>[^:^/]*)(?::(?P<port>[^/|^?]*))?(?:/(?P<path>.*))?")
RE_CONN_TEMPLATE = re.compile(r"(?:(?P<user>[^/]*)/(?P<password>[^@]*)@//)?(?P<dsn>.*)")

OracleUriParts = namedtuple('OracleUriParts', 'user,password,dsn'.split(','))

class OracleConnMixin:
    def _parse_uri(self, conn_uri):
        """Returns UriParts tuple
        
        Arguments:
            conn_uri {str} -- [description]
        
        Returns:
            [UriParts] -- Parts of uri
        """
        match = RE_CONN_TEMPLATE.match(conn_uri)
        m = match.group
        return OracleUriParts(m('user'), m('password'), m('dsn'))


class OracleDb(SynDataDriver, OracleConnMixin):

    autoclose = True

    def is_connected(self):
        return self.engine is not None
    
    def _setup_cursor(self, cursor):
        cursor.rowfactory = makeDictFactory(cursor)
        return cursor

    def _connect(self):
        user, password, dsn = self.uri_parts
        print("DSN: ", user, password, dsn)
        self.engine = cx_Oracle.connect(user, password, dsn, encoding="UTF-8")
    

# Thanks for: https://stackoverflow.com/a/35046018
def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]
    def createRow(*args):
        return dict(zip(columnNames, args))
    return createRow

def makeNamedTupleFactory(cursor):
    columnNames = [d[0].lower() for d in cursor.description]
    import collections
    Row = collections.namedtuple('Row', columnNames)
    return Row