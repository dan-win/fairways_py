import asyncio
import aioredis

from fairways.io.generic.dbi import (BaseQuery, ReaderMixin)
# Re-export:
from fairways.io.asyn.redis import RedisDriver

import logging
log = logging.getLogger(__name__)

class RedisConsumer(BaseQuery, ReaderMixin):
    template_class = dict
    
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
