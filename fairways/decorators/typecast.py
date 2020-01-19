"""Decorators to implement type conversion via single method in a class (fromtype and/or intotype)
"""

class FromTypeMixin:
    """Use this mixing during definition of your class.
    Then you could use `@typecast.fromtype` decorator when defining methods for typecasting.
    """

    converters_registry = {}

    @classmethod
    def fromtype(cls, source):
        key1 = cls.__qualname__
        source_type = type(source)
        key2 = source_type
        reg = FromTypeMixin.converters_registry
        try:
            method = reg[key1][key2]
        except Exception:
            raise TypeError(f"Cannot convert {cls.__name__} from {source_type}")
        instance = cls()
        method(instance, source)
        return instance


class IntoTypeMixin:
    """Use this mixing during definition of your class.
    Then you could use `@typecast.intotype` decorator when defining methods for typecasting.
    """

    converters_registry = {}

    def intotype(self, dest_type):
        key1 = self.__class__.__qualname__
        key2 = dest_type
        reg = IntoTypeMixin.converters_registry
        try:
            method = reg[key1][key2]
        except Exception:
            raise TypeError(f"Cannot convert {self.__class__.__name__} into {dest_type}")
        # instance = dest_type()
        return method(self, dest_type)


class fromtype:
    """`@typecast.fromtype` decorator.
    """
    counter = 0
    def __init__(self, source_type):
        self.source_type = source_type
    
    def __call__(self, f):
        print("FUNC:", f.__class__, f.__qualname__)
        reg = FromTypeMixin.converters_registry
        # Get class name from qualified name of method:
        key1 = ".".join(f.__qualname__.split('.')[:-1])
        key2 = self.source_type
        # FromTypeMixin.converters_registry[key]
        if key1 not in reg:
            reg[key1] = {}
        root = reg[key1]
        if key2 in root:
            raise TypeError(f"Converter for {key1} from {key2} already registered")
        root[key2] = f
        return f

class intotype:
    """`@typecast.intotype` decorator.
    """
    counter = 0
    def __init__(self, dest_type):
        self.dest_type = dest_type
    
    def __call__(self, f):
        print("FUNC:", f.__class__, f.__qualname__)
        reg = IntoTypeMixin.converters_registry
        # Get class name from qualified name of method:
        key1 = ".".join(f.__qualname__.split('.')[:-1])
        key2 = self.dest_type
        # FromTypeMixin.converters_registry[key]
        if key1 not in reg:
            reg[key1] = {}
        root = reg[key1]
        if key2 in root:
            raise TypeError(f"Converter for {key1} to {key2} already registered")
        root[key2] = f
        return f

