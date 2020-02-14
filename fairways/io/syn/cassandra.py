# -*- coding: utf-8 -*-
"""Driver facade for ScyllaDB/Cassandra.

Requires `DataStax Driver for Apache Cassandra <https://github.com/datastax/python-driver/>`_.

"""

from cassandra.cluster import Cluster as CassandraCluster
from cassandra.auth import PlainTextAuthProvider as CassandraPlainTextAuthProvider
from cassandra.query import dict_factory as cassandra_dict_factory
from cassandra.policies import (DCAwareRoundRobinPolicy as _DCAwareRoundRobinPolicy, RoundRobinPolicy as _RoundRobinPolicy)
import re
from collections import namedtuple

from .base import (SynDataDriver, UriConnMixin)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# UriParts = namedtuple('UriParts', 'scheme,user,password,host,port,path,params'.split(','))
CassandraUriParts = namedtuple('UriParts', 'scheme,user,password,cluster_points,port,keyspace,params'.split(','))

class CassandraConnMixin(UriConnMixin):
    """Parser for connection string.
    Works with URI like  `cassandra://user:password@host1--host2--host3:9160/keyspace1`.
    """
    def _parse_uri(self, conn_uri):
        uri_parts = UriConnMixin._parse_uri(self, conn_uri)
        cluster_points = uri_parts.host.split("--")
        keyspace = uri_parts.path
        return CassandraUriParts(
            uri_parts.scheme,
            uri_parts.user,
            uri_parts.password,
            cluster_points,
            uri_parts.port,
            keyspace,
            uri_parts.params)

class Cassandra(SynDataDriver, CassandraConnMixin):
    """ScyllaDB/Cassandra driver.

    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "cassandra://user:password@host:9160/keyspace1")
    :type env_varname: str
    """

    #: Do not close connection after single request
    autoclose = False

    def __init__(self, env_varname):
        """Constructor method
        """
        super().__init__(env_varname)
        self.session = None

    def is_connected(self):
        """Connection status
        """
        # TODO: Cassandra: Is there some way to check connection?
        return self.engine is not None

    def close(self):
        """Close all connections.
        """
        if self.is_connected():
            cluster = self.engine
            cluster.shutdown()
            self.engine = None

    def _setup_cursor(self, cursor):
        cursor.rowfactory = makeDictFactory(cursor)
        return cursor

    def _connect(self):
        scheme,user,password,cluster_points,port,keyspace,params = self.uri_parts
        auth_provider = None
        if user and password:
            auth_provider = CassandraPlainTextAuthProvider(username=user, password=password)
        local_dc = self.qs_params.get("local_dc", "")
        if local_dc:
            load_balancing_policy = _DCAwareRoundRobinPolicy(local_dc="datacenter1")
        else:
            load_balancing_policy = _RoundRobinPolicy()
        cluster = CassandraCluster(
            list(cluster_points), 
            port=port,
            auth_provider=auth_provider,
            load_balancing_policy=load_balancing_policy,
            )

        session = cluster.connect(keyspace) # Note that keyspace could be None after parsing regexp

        request_timeout = self.qs_params.get('request_timeout')
        if request_timeout is not None:
            request_timeout = float(request_timeout)
            session.request_timeout = request_timeout

        session.row_factory=cassandra_dict_factory
        session.default_fetch_size=None # Override default 5000 limit

        self.engine = cluster
        self.session = session
    
    def _query(self, cql):
        try:
            self._ensure_connection()
            rows = self.session.execute(cql)
            return list(rows) # By defaul returned object has type cassandra.cluster.ResultSet whit can be casted to list
        except Exception as e:
            log.error("DB operation error: %r at %s; %s", e, self.db_name, cql)
            raise
        finally:
            if self.autoclose:
                self.close()


    def fetch(self, cql):
        """Fetch data from resource
        
        :param cql: CQL script to fetch data
        :type cql: str
        :return: Result 
        :rtype: List[Dict]
        """
        log.debug("Cassandra: CQL fetch: %s", cql)
        return self._query(cql)

    def change(self, cql):
        """Change data on resource
        
        :param cql: Script to fetch data
        :type cql: str
        """
        log.debug("Cassandra: CQL change: %s", cql)
        return self._query(cql)


