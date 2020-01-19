Typecast
==========

Decorators to implement type conversion via single method in a class.
Avoid a lot of methods like `as_dict`, `into_str`, `from_dict` and so on.
Inspired by handy `Rust traits From/Into <https://doc.rust-lang.org/std/convert/trait.From.html>`_.
Note that the type casting can be irreversible (e.g. some class can be represent as a string but reverse conversion can not be possible).

Quick example:

    .. code-block:: python

        # From:

        class CustomClass:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return f"{self.__class__.__name__}:{self.name}"

        class MyClass(typecast.FromTypeMixin):

            def __init__(self, value=None):
                self.value = value

            @typecast.fromtype(int)
            def _from_int(self, value):
                self.value = f"From int: {value}"

            @typecast.fromtype(str)
            def _from_str(self, value):
                self.value = f"From str: {value}"

            @typecast.fromtype(dict)
            def _from_dict(self, value):
                self.value = f"From dict: {value}"

            @typecast.fromtype(CustomClass)
            def _from_obj(self, value):
                self.value = f"From CustomClass: {value}"
            
            def __str__(self):
                return self.value

        MyClass.fromtype(1).value == 'From int: 1'
        MyClass.fromtype("Text").value == 'From str: Text'
        MyClass.fromtype(dict(a=1)).value == "From dict: {'a': 1}"
        MyClass.fromtype(CustomClass("objectName")).value == \
            'From CustomClass: CustomClass:objectName'

        # Into:

        class MyClass(typecast.IntoTypeMixin):

            def __init__(self, value=None):
                self.value = value

            @typecast.intotype(int)
            def _into_int(self, value):
                return int(self.value)

            @typecast.intotype(str)
            def _into_str(self, value):
                return str(self.value)

            @typecast.intotype(dict)
            def _into_dict(self, value):
                return {"value": self.value}

            @typecast.intotype(CustomClass)
            def _into_obj(self, value):
                return CustomClass(self.value)
            
            def __str__(self):
                return self.value

        MyClass("1").intotype(int) == 1
        MyClass(1).intotype(str) == '1'
        str(MyClass("1").intotype(dict)) == str({'value': '1'})
        str(MyClass("1").intotype(CustomClass)) \
            == 'CustomClass:1'


.. automodule:: fairways.decorators.typecast
   :members:
