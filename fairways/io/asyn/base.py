from fairways.io.generic import (DataDriver, UriConnMixin, FileConnMixin)

import asyncio

import logging

log = logging.getLogger()

class AsyncDataDriver(DataDriver):

    async def _ensure_connection(self):
        if self.is_connected():
            return
        log.warning("Restoring DB connection: {}".format(self.db_name))
        await self._connect()

    async def _connect(self):
        raise NotImplementedError(f"Override _connect for {self.__class__.__name__}")
    
    async def close(self):
        if self.is_connected():
            await self.engine.close()
            self.engine = None

    async def fetch(self,sql):
        try:
            await self._ensure_connection()
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
            await self._ensure_connection()
            await self.engine.execute(sql)
            log.debug("EXECUTING...........")
            await self.engine.commit()
        except Exception as e:
            log.error("DB operation error: {} at {}; {}".format(e, self.db_name, sql))
            raise
        finally:
            if self.autoclose:
                await self.close()

    # Inherited (note: sync method, acts as a proxy to coroutine):
    # def get_records(self, query_template, **params):

    # Inherited:
    # def execute(self, query_template, **params):
