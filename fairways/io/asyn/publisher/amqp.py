import asyncio
import aio_pika

from fairways.io.generic.dbi import (BaseQuery, WriterMixin)
# Re-export:
from fairways.io.asyn.amqp import AmqpDriver

import logging
log = logging.getLogger(__name__)

class AmqpPublisher(BaseQuery, WriterMixin):
    template_class = dict

    def _transform_params(self, params):
        options = self.template
        message_body = params["message"]
        headers = params.get("headers", {})
        params = dict(
            exchange=options["exchange"],
            routing_key=options.get("routing_key", None),
            body=message_body,
            headers=headers
        )
        return params


