from faker import Faker
fake = Faker('en_GB')
from faker.providers import date_time
fake.add_provider(date_time)
from faker.providers import BaseProvider

import random

_fake_mode = False

def fake_mode():
    global _fake_mode
    _fake_mode = True

from enum import Enum


_fake_db_registry = {}

RECORDS_COUNT = 20

class Model:
    def _scope(self):
        return self.db_ti.__class__
    
    def task_by_name(self, name):
        return getattr(
            self._scope,
            name
        )

    def __init__(self, db_task_item, struct):
        self.db_ti = db_task_item
        self.struct = struct
        self.data = []
    
    def build(self):



    def get(self):
        if not self.data:
            self.data = self.build()
        return self.data


class FakeField:
    def __init__(self):
        pass
    def value(self):
        raise NotImplementedError

class NameField:
    def value(self):
        return fake.name()

class YearField:
    def value(self):
        return fake.year()

class EnumField:
    def __init__(self, values):
        self.values = list(values)

    def value(self):
        return random.choice(self.values)



def fake_model_factory(enum_cls, model):
    m = dict(model)
    template = {}
    # Build template
    for field, ftype in m.items():
        if ftype in ()
    buffer = []


class FakeFK:
    """
    Foreign key provider
    """
    def __init__(self, query_name, field):
        self.query

    def foo(self):
        return 'bar'
