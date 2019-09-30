# -*- coding: utf-8 -*-
fake = None

def init_faker():
    """
    Avoid heavy operations when not in fake mode
    """
    global fake
    from faker import Faker
    fake = Faker('en_GB')
    from faker.providers import (date_time, internet, )
    fake.add_provider(date_time)
    fake.add_provider(internet)

import os
import re
import random
import uuid
import json

from enum import Enum

from inspect import isclass
# import invregex

import logging
log = logging.getLogger(__name__)

_fake_db_registry = {}
_db_task_set = None # This is reference to the singleton

RECORDS_COUNT = 5

class FakeDBDriver:

    def __init__(self, db_ts_class):
        self.registry = {}
        self.db_ts_class = db_ts_class
        self.models = Models(self.registry)

    def add_model(self, model_name, sql_key, meta):
        model = Model(self.models, model_name, meta)
        self.registry[sql_key] = model
    
    def fake_connection(self, *args, **kwargs):
        """Build fake data for models
        
        Returns:
            [type] -- [description]
        """

        for model in self.registry.values():
            model.build(resolve_fk=True)

        return self
    
    def __call__(self, *args, **kwargs):
        """Emulate connection, returns self for further calls of get_records, etc...
        
        Returns:
            [type] -- [description]
        """
        return self.fake_connection(*args, **kwargs)

    def get_records(self, sql, **sql_params):
        model = self.registry[sql]
        return model.get()
        # for _ in range(1, RECORDS_COUNT):
        #     return "scanning task: ", result, type(result)

class MODES:
    PROD = ""
    USE_FAKE = "fake"
    USE_FIXTURE = "fixture"


class fixture:
    """
    Decorator with fake data form QueriesSet
    """
    def __init__(self, 
            test_mode_attr="FAKE_DB_MODE", 
            fixture_attr="DB_FIXTURE_DATA", 
            fixture_file=None, 
            *args, **kwargs):

        """[summary]
        
        Keyword Arguments:
            test_mode {bool} -- Switches fake mode on (default: {False})
        """

        fx_data_serialized = os.getenv(fixture_attr, None)
        fixture = None
        if fx_data_serialized:
            fixture = json.loads(fx_data_serialized)


        self.test_mode = os.getenv(test_mode_attr, MODES.PROD)
        self.fixture = fixture
        self.fixture_file = fixture_file

    
    def __call__(self, cls, *args, **kwargs):
        # # def wrapper(*args, **kwargs):
        # test_mode = self.test_mode
        # fixture = self.fixture
        # fixture_file = self.fixture_file

        # if test_mode == MODES.USE_FAKE:
        #     log.info("********************************** fixture: USE_FAKE ********************************** ")
        #     init_faker()
        #     fake_driver = FakeDBDriver(cls)
        #     for k, v in cls.__dict__.items():
        #         log.info("...Scanning... %s, %s, %s", k, type(v), issubclass(v.__class__, Enum))
        #         # Replace db driver:
        #         if k.startswith("_") or k.endswith("_"):
        #             continue
        #         if issubclass(v.__class__, Enum):
        #             log.info("%s created in a test mode", k, v)

        #             sql, meta = v.sql, v.meta
        #             model_name = k
        #             sql_key = sql
        #             fake_driver.add_model(model_name, sql_key, meta)
        #             v.driver = fake_driver
        #             # setattr(cls, k, (sql, env_alias, fake_driver, meta))

        # elif test_mode == MODES.USE_FIXTURE:
        #     log.info("********************************** fixture: USE_FIXTURE ********************************** ")
        #     if fixture_file:
        #         with open(fixture_file, 'r') as f:
        #             s = f.read()
        #             fx_data = json.loads(s.decode('utf-8'))
        #     elif fixture:
        #         fx_data = fixture
        #     else:
        #         raise TypeError("Neither variable nor file were specified for fixture data!")
        #     # Define new class:

        #     cls_name = "{}Fixture".format(cls.__name__)
        #     attrs = {}
        #     for name, response in fx_data.items():
        #         attrs[name] = DbResponseFixture(name, response)
        #     fx_class = type(cls_name, (object,), attrs)
        #     return fx_class


        return cls


class Models:
    def __init__(self, models_list):
        self.models = models_list

    def find_by_name(self, model_name):
        for model in self.models.values():
            if model_name == model.name:
                return model
        raise KeyError("Model with name '{}' not found!".format(model_name))


class FKError(Exception):
    """ Cannot resolve foreign key """
    

class Model:

    def __init__(self, models, model_name, meta):
        self.parent = models
        self.name = model_name
        self.meta = meta
        self.data = []
    
    def build(self, resolve_fk=True, rows_count=RECORDS_COUNT):
        parent = None
        if resolve_fk:
            parent = self.parent

        fakers = {}
        for row in self.meta:
            try:
                fname, ffactory = row
            except ValueError as e:
                raise ValueError("Parsing error: {}; at row: '{}'".format(e, row))
            if ffactory is None:
                ffactory = ConstField(None)
            elif isinstance(ffactory, (str, bool, int, float, dict)):
                local_value = ffactory
                ffactory = ConstField(local_value)
            elif isinstance(ffactory, ChildModel):
                ffactory = Model(self.parent, "{}.{}".format(self.name, fname), ffactory.meta)
            elif isclass(ffactory):
                ffactory = ffactory()
            # else:
            #     raise TypeError("Unknown definition type: {!r}".format(ffactory))
            fakers[fname] = ffactory

        for i in range(0, rows_count):
            row = {}
            for rec in self.meta:
                fname = rec[0]
                row[fname] = fakers[fname].value(self)
            self.data.append(row)

    def get(self, resolve_fk=True, rows_count=RECORDS_COUNT):
        if not self.data:
            self.build(resolve_fk, rows_count)
        return self.data
    
    def value(self, parent_model):
        """
        Model itself can act as a faker (returns single instance)
        """
        return self.get().pop(-1)
    
    def get_adjacent(self, model_name):
        return self.parent.find_by_name(model_name)

class ChildModel:
    def __init__(self, meta):
        self.meta = list(meta)


class FakeField:
    def __init__(self):
        pass
    def value(self, model):
        raise NotImplementedError

class ConstField():
    def __init__(self, value):
        self._value = value
    def value(self, model):
        return self._value

class AutoIncField:
    def __init__(self):
        self.last_value = 0
    def value(self, model):
        self.last_value += 1
        return self.last_value

class Uuid4Field:
    def value(self, model):
        return str(uuid.uuid4())


# class RegExField:
#     def __init__(self, regex):
#         self.possible_strings = list(invregex.invert(regex))
#     def value(self, model):
#         return random.choice(self.possible_strings)

class SlugField:
    def __init__(self, template):
        self.template = template
    def value(self, model):
        return self.template.format(fake.slug())

class TemplateField:
    def __init__(self, template):
        self.template = template
        self.names = re.findall("\{([^\}]*)\}", template)

    def render(self):
        buff = self.template
        for name in self.names:
            value = eval("fake.{}()".format(name))
            # value = getattr(provider, method_name)()
            buff = buff.replace("{{{}}}".format(name), value)
        return buff

    def value(self, model):
        return self.render()


class NameField(FakeField):
    def value(self, model):
        return fake.name()

class YearField(FakeField):
    def value(self, model):
        return fake.year()

class EnumField(FakeField):
    def __init__(self, values):
        if isinstance(values, Enum):
            enum = values
            values = [e.value for e in enum]
        self.values = list(values)

    def value(self, model):
        return random.choice(self.values)

class FK(FakeField):
    """
    Foreign key provider
    """
    def __init__(self, model_name, field, one2one=False):
        self.model_name = model_name
        self.field = field
        self.buff = None
        self.one2one = one2one
        self.seen = set()

    def value(self, model):
        lookup_model = model.get_adjacent(self.model_name)
        field = self.field
        if not self.buff:
            self.buff = [r[field] for r in lookup_model.get()]
        if self.one2one:
            value = self.buff.pop(-1)
            while value in self.seen:
                try:
                    value = self.buff.pop(-1)
                except IndexError:
                    raise IndexError(
                        "Possible values of foreign key exhausted: {}:{}, seen values: {}".format(
                            self.model_name,
                            self.field,
                            self.seen
                        ))
            self.seen.add(value)
            return value
        return random.choice(self.buff)


# def fake_model_factory(enum_cls, model):
#     m = dict(model)
#     template = {}
#     # Build template
#     for field, ftype in m.items():
#         if ftype in ()
#     buffer = []



class DbResponseFixture:
    def __init__(self, name, response_dict):
        self.name = name
        self.response_dict = response_dict

    def get_records(self, **sql_params):
        """ Return fixture data to simulate DB response"""
        return self.response_dict
    
    def execute(self, *args, **kwargs):
        """ Dummy execute method"""
        log.info("Fake execute: [%s] %s %s", self.name, args, kwargs)
        pass



# class DbTaskSetFixture:


#     def __init__(self, fx_data):
#         """Creates new instance of DB task with fixture responses (read-only dataset)
#         Emulates behaviour of io.DBATestkSet
#         Note: class is based on Python Enum so
#         __init__ blesses a single member of enumeration
#         (See more about Python Enum class)
        
#         Arguments:
#             fx_data - dict where values are names of objects and values are responses of related get_records()
#         """
#         # self.task_id = 'TASK_ID_DB_FETCH_' + self.name.upper()
#         self.registry = {}
#         for name, response in fx_data.items():
#             self.registry[name] = DbResponseFixture(response)    

#     def __getattribute__(self, name):
#         if name in self.registry:
#             return self.registry[name]
#         return object.__getattribute__(self, name)



if __name__ == "__main__":

    import os, sys

    path = os.path.abspath(os.path.join("./.."))

    if path not in sys.path:
        sys.path.append(path)

    from fairways.io import (QueriesSet)

    @fixture(True)
    class TestDbSet(QueriesSet):
        TEST_1 = (
            "select * from table1",
            "NODB", 
            lambda n: n,
            (
                ("id",      AutoIncField),
                # "name":   NameField,
                ("name",    TemplateField("Film {last_name}")),
                ("year",    YearField),
                ("tag",     EnumField(['q','w','e'])),
                ("seo_alias", TemplateField("seo_path/{slug}-{year}/"))
                # "seo_alias": SlugField("{}/")
            )
        )

        TEST_2 = (
            "select * from table2",
            "NODB", 
            lambda n: n,
            (
                ("id",      AutoIncField),
                ("fk_id",      FK("TEST_1", "id")),
                ("flag",   True),
                ("desc",    TemplateField("Film {last_name}")),
            )
        )

    log.info("Result %s", TestDbSet.TEST_1.get_records())
    log.info("Result %s", TestDbSet.TEST_2.get_records())