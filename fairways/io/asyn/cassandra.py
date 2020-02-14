# -*- coding: utf-8 -*-
"""Driver facade for ScyllaDB/Cassandra.

Requires `DataStax Driver for Apache Cassandra <https://github.com/datastax/python-driver/>`_.

Due to specific implementation of async mode in DataStax driver (with callbacks), async implementation derived from sync driver here.
"""
from fairways.io.syn.cassandra import Cassandra as SynCassandra
import asyncio
import threading
import random

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster as CassandraCluster
from cassandra.query import SimpleStatement
from cassandra.auth import PlainTextAuthProvider as CassandraPlainTextAuthProvider
from cassandra.query import dict_factory as cassandra_dict_factory
from cassandra.policies import (DCAwareRoundRobinPolicy as _DCAwareRoundRobinPolicy, RoundRobinPolicy as _RoundRobinPolicy)
from cassandra.io.asyncioreactor import AsyncioConnection

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Cassandra(SynCassandra):

    async def _query(self, cql):
        try:
            self._ensure_connection()
            # rows = self.session.execute(cql)
            # return list(rows) # By defaul returned object has type cassandra.cluster.ResultSet whit can be casted to list
            cql = SimpleStatement(
                cql, consistency_level=1)

            event = threading.Event()
            results = []
            future = self.session.execute_async(cql)

            def log_results(res, level='debug'):
                if res:
                    results.extend(res[:])
                log.info("Result: %s", res)
                event.set()

            def log_error(exc, query):
                import sys, traceback
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log.error("Query '%s' failed: %r; %s", query, exc, "\n".join(traceback.format_exception(exc_type, exc_obj,
                                        exc_tb)))
                event.set()
                raise exc

            future.add_callbacks(
                callback=log_results, callback_kwargs={'level': 'debug'},
                errback=log_error, errback_args=(cql,))

            # await event.wait()
            while not event.is_set():
                await asyncio.sleep(random.random())

            return results

        except Exception as e:
            log.error("DB operation error: %r at %s; %s", e, self.db_name, cql)
            raise
        finally:
            if self.autoclose:
                self.close()

    async def fetch(self, cql):
        """Fetch data from resource
        
        :param cql: CQL script to fetch data
        :type cql: str
        :return: Result 
        :rtype: List[Dict]
        """
        log.debug("Cassandra: CQL fetch: %s", cql)
        return await self._query(cql)

    async def change(self, cql):
        """Change data on resource
        
        :param cql: Script to fetch data
        :type cql: str
        """
        log.debug("Cassandra: CQL change: %s", cql)
        return await self._query(cql)

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
            connection_class=AsyncioConnection
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

# # =============

# session = cluster.connect()
# future = self.session.execute_async(cql)
# event = asyncio.Event()
# results = []

# def log_results(res, level='debug'):
#     results.extend(res[:])
#     log.log(level, "Result: %s", row)

# def log_error(exc, query):
#     log.error("Query '%s' failed: %s", query, exc)

# future.add_callbacks(
#     callback=log_results, callback_kwargs={'level': 'info'},
#     errback=log_error, errback_args=(query,))

# await event.wait()

# return results