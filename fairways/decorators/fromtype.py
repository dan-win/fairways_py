
from collections import defaultdict

# from typing import Dict, Mapping, Callable


# transform_rules_map: Dict[str, Callable]...




class FromTypeMixin:

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



class implement:
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


if __name__ == "__main__":
    class CustomClass:
        def __init__(self, name):
            self.name = name
        def __str__(self):
            return f"{self.__class__.__name__}:{self.name}"

    class MyClass(FromTypeMixin):

        def __init__(self, value=None):
            self.value = value

        @implement_from(int)
        def _from_int(self, value):
            self.value = f"From int: {value}"

        @implement_from(str)
        def _from_str(self, value):
            self.value = f"From str: {value}"

        @implement_from(dict)
        def _from_dict(self, value):
            self.value = f"From dict: {value}"

        @implement_from(CustomClass)
        def _from_obj(self, value):
            self.value = f"From CustomClass: {value}"
        
        def __str__(self):
            return self.value

    print(MyClass.fromtype(1))
    print(MyClass.fromtype("Text"))
    print(MyClass.fromtype(dict(a=1)))
    print(MyClass.fromtype(CustomClass("objectName")))
