

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


    # def intotype(self, dest_type):
    #     key1 = cls.__qualname__
    #     key2 = type(dest_type)
    #     reg = FromTypeMixin.converters_registry
    #     try:
    #         method = reg[key1][key2]
    #     except Exception:
    #         raise TypeError(f"Cannot convert {self.__class__.__name__} into {dest_type}")
    #     instance = dest_type()
    #     method(instance, source)
    #     return instance


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

