import asyncio

import logging

log = logging.getLogger(__name__)

class AsyncDbDriver:

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]
    
    def is_connected(self):
        raise NotImplementedError("Override is_connected in descendants!")

    async def _ensure_connection(self):
        if self.is_connected():
            return
        log.warning("Restoring DB connection: {}".format(self.db_name))
        await self._connect()

    # async def _connect(self):
    #     db_filename = self.conn_str
    #     engine = await aiosqlite.connect(db_filename)
    #     engine.row_factory = dict_factory
    #     engine.isolation_level = "IMMEDIATE"
    #     self.engine = engine
    
    async def close(self):
        if self.is_connected():
            await self.engine.close()
            self.engine = None

    def __init__(self, env_varname='DB_CONN', default=":memory:"):
        self.conn_str = os.getenv(env_varname, default)
        self.engine = None
        assert self.conn_str, "SqLite error: you should specify either environment variable or default value for database file name"
            
    async def fetch(self,sql):
        try:
            await self._connect()
            async with self.engine.execute(sql) as cursor:
                return await cursor.fetchall()
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if self.autoclose:
                await self.close()

    async def change(self, sql):
        try:
            await self._connect()
            await self.engine.execute(sql)
            await self.engine.commit()
            return None
        except Exception as e:
            log.error("DB operation error: {} at {}; {}".format(e, self.db_name, sql))
            raise
        finally:
            if self.autoclose:
                await self.close()

    def get_records(self, query_template, **params):
        """
        Proxy method: Return coroutine which returns list of records
        Result shoul be called with "await" syntax
        """
        # Convert all iterables to lists to 
        query = query_template.format(**params).replace('\n', " ").replace("\"", "\'")
        # log.debug("SQL: {}".format(query))
        return self.fetch(query)

    def execute(self, query_template, **params):
        """
        Proxy method: Return coroutine which modifies records in storage.
        Result shoul be called with "await" syntax
        """
        query = query_template.format(**params)
        # log.debug("SQL: {}".format(query))
        return self.change(query)
