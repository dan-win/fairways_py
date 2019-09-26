from .base import AsyncDbDriver
# Should provice async methods .fetch, .execute

import asyncio
import aioredis

import logging
log = logging.getLogger(__name__)

class RedisDriver(AsyncDbDriver):
    default_conn_str = "redis://localhost"
    autoclose = True

    def is_connected(self):
        return self.engine is not None

    async def _connect(self):
        conn_str = self.conn_str
        engine = await aioredis.create_redis_pool(conn_str)
        self.engine = engine

    async def close(self):
        # Details: https://github.com/aio-libs/aioredis
        if self.is_connected():
            self.engine.close()
            await self.engine.wait_closed()
            self.engine = None

    def get_records(self, _, **params):
        """
        Return data
        """
        return self.__redis_cmd(params)


    def execute(self, _, **params):
        """
        Return data
        """
        return self.__redis_cmd(params)

    async def __redis_cmd(self, params):
        command = params["command"].lower()
        key = params["key"]
        args = params.get("args", [])
        kwargs = params.get("kwargs", {})
        try:
            await self._ensure_connection()
            connection = self.engine
            command_handler = getattr(connection, command)
            return await command_handler(key, *args, **kwargs)
        except Exception as e:
            log.error("Redis operation error: {} at {};".format(e, params))
            raise
        finally:
            if self.autoclose:
                await self.close()
