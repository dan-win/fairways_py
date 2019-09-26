import asyncio
import aio_pika

from .base import Publisher
# Re-export:
from fairways.io.asyn.amqp import AmqpDriver

import logging
log = logging.getLogger(__name__)

class AmqpPublisher(Publisher):

    def _transform_params(self, params):
        options = self.template
        message_body = params["message"]
        params = dict(
            exchange=options["exchange"],
            routing_key=options.get("routing_key", None),
            body=message_body
        )
        return params


