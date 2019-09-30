import asyncio
import aioredis

from fairways.io.generic.dbi import (BaseQuery, ReaderMixin)
# Re-export:
from fairways.io.asyn.amqp import AmqpDriver

import logging
log = logging.getLogger(__name__)

class AmqpConsumer(BaseQuery, ReaderMixin):
    template_class = dict
    
    def _transform_params(self, params):
        options = self.template
        params = dict(
            queue=options["queue"],
        )
        return params
