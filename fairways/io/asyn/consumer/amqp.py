import asyncio
import aioredis

from .base import Consumer
# Re-export:
from fairways.io.asyn.amqp import AmqpDriver

import logging
log = logging.getLogger(__name__)

class AmqpConsumer(Consumer):
    
    # def _transform_params(self, params):
    #     return params

    def _transform_params(self, params):
        options = self.template
        params = dict(
            queue=options["queue"],
        )
        return params
