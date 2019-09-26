from fairways.io.generic.dbi import Query

import asyncio

from typing import Dict
# class MessageMeta:
#     pass

class Consumer(Query):

    def __init__(self, template: Dict[str, str], env_conf, driver, meta=None):
        """Creates new instance of IO task 
        
        Arguments:
            template {dict} -- Template (constant part) of query
            env_conf {str} -- Name of environment variable wich holds config
            driver {DbDriver} -- DbDriver subclass
            meta {dict} -- Any QA data to store with the task instance
        """
        super().__init__(template, env_conf, driver, meta)

    def execute(self, **params):
        raise TypeError("Not allowed!")


