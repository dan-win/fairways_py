import asyncio
import aioredis

from .base import Consumer
# Re-export:
from fairways.io.asyn.redis import RedisDriver

import logging
log = logging.getLogger(__name__)

class RedisConsumer(Consumer):
    
    # def _transform_params(self, params):
    #     return params

    def _transform_params(self, params):
        options = self.template
        params = dict(
            command=options["command"],
            key=options["key"],
        )
        if options.get("timeout"):
            params.update(dict(
                timeout=options["timeout"]
            ))
        return params
