fake = None

def init_faker():
    """
    Avoid heavy operations when not in fake mode
    """
    global fake
    from faker import Faker
    fake = Faker('en_GB')
    from faker.providers import (date_time, internet)
    fake.add_provider(date_time)
    fake.add_provider(internet)

import re
import random


from enum import Enum

from inspect import isclass
# import invregex

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


class fixture:
    """
    Decorator with fake data form DbTaskSet
    """
    def __init__(self, test_mode=False, *args, **kwargs):
        """[summary]
        
        Keyword Arguments:
            test_mode {bool} -- Switches fake mode on (default: {False})
        """
        self.test_mode = test_mode
        print("Decorator __init__", args, kwargs)

    
    def __call__(self, cls, *args, **kwargs):
        # def wrapper(*args, **kwargs):
        print("__call__", cls)
        test_mode = self.test_mode

        if test_mode:
            init_faker()
            fake_driver = FakeDBDriver(cls)
            for k, v in cls.__dict__.items():
                print("...Scanning...", k, type(v), issubclass(v.__class__, Enum))
                # Replace db driver:
                if k.startswith("_") or k.endswith("_"):
                    continue
                if issubclass(v.__class__, Enum):
                    print("{} created in a test mode: v".format(k, v))

                    sql, meta = v.sql, v.meta
                    model_name = k
                    sql_key = sql
                    fake_driver.add_model(model_name, sql_key, meta)
                    v.driver = fake_driver
                    # setattr(cls, k, (sql, env_alias, fake_driver, meta))

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
    
    def build(self, resolve_fk=True):
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
            if isinstance(ffactory, (str, bool, int, float)):
                local_value = ffactory
                ffactory = ConstField(local_value)
            if isclass(ffactory):
                ffactory = ffactory()
            fakers[fname] = ffactory

        for i in range(0, RECORDS_COUNT):
            row = {}
            for rec in self.meta:
                fname = rec[0]
                # print('--->>>', fname, ffactory)
                row[fname] = fakers[fname].value(self)
            self.data.append(row)

    def get(self, resolve_fk=True):
        if not self.data:
            self.build(resolve_fk)
        return self.data
    
    def get_adjacent(self, model_name):
        return self.parent.find_by_name(model_name)

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
        print("NAMES FOUND: ", self.names)

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
    def __init__(self, model_name, field):
        self.model_name = model_name
        self.field = field

    def value(self, model):
        lookup_model = model.get_adjacent(self.model_name)
        field = self.field
        values = [r[field] for r in lookup_model.get()]
        return random.choice(values)


# def fake_model_factory(enum_cls, model):
#     m = dict(model)
#     template = {}
#     # Build template
#     for field, ftype in m.items():
#         if ftype in ()
#     buffer = []

if __name__ == "__main__":

    import os, sys

    path = os.path.abspath(os.path.join("./.."))

    if path not in sys.path:
        sys.path.append(path)

    from hostapi.io import (DbTaskSet)

    @fixture(True)
    class TestDbSet(DbTaskSet):
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

    print("Result", TestDbSet.TEST_1.get_records())
    print("Result", TestDbSet.TEST_2.get_records())