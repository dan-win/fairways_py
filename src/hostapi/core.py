# -*- coding: utf-8 -*-

class Heap:
    """
    Replacer for Airflow "xcom" which doesn't allow large data buffering.
    """

    def __init__(self, engine):
        self.engine = engine

    def push(self, datakey, data):
        self.engine.push(datakey, data)

    def pull(self, datakey):
        return self.engine.pull(datakey)


    def store(self, func):
        """
        Decorator for task callable - store result in heap
        Key === task_id
        """
        def wrapper(context):
            new_context = func(context)
            # log.debug("\nIO MESSAGE ({})\n: {}\n===\n".format(func.__name__, new_context))
            self.push(func.__name__, new_context)
            return new_context
             # Avoid xcom_push for any large data!
        return wrapper
