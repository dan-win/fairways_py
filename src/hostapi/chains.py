# TO-DO: move to rust with multiprocessing!
class Chain:
    """
    Chainable sequence to route data amoung "processors" (any callable)
    """
    def __init__(self, some_data):
        if callable(some_data):
            some_data = some_data(None)
        self.data = some_data
    
    def then(self, method):
        """
        """
        arg = self.data
        result = method(arg)
        return Chain(result)
    
    def all(self, *methods_list):
        """
        Executes all methods, puts results into array
        """
        results = []
        for method in methods_list:
            result = method(self.data)
            results.append(result)
        return Chain(results)

    def merge(self, *methods_list):
        """
        Executes all methods, merges results into dict
        """
        results = {}
        for method in methods_list:
            result = method(self.data)
            results.update(result)
        return Chain(results)

    @property
    def value(self):
        return self.data


