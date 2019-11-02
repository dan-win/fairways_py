from fairways import (taskflow, funcflow)
from abc import abstractmethod
from typing import Callable
from .utils import module_of_callable

ff = funcflow.FuncFlow

class DryRunMiddleware:

    def __init__(self, chain: taskflow.Chain) -> None:
        self.step = 1
        self.results = []
        self.chain = chain
        print("1")


    @abstractmethod
    def inspect(self, method: Callable, chain:taskflow.Chain, step: int) -> None:
        pass


    def __call__(self, method, data, **kwargs):
        print("2")
        self.results.append(
            self.inspect(method, self.chain, self.step)
        )
        # print("\nSTEP #{} [{}], data after:\n {!r}".format(self.step, method.__name__, result))
        self.step += 1
        return data
    
    def walk(self, data=None):
        data = data or {}
        for handler in self.chain.handlers:
            self(handler.method, data)
        return self.results


class StateShapeExplorer(DryRunMiddleware):

    # def __init__(self, chain: taskflow.Chain) -> None:
    #     self.state_shape = {}

    @staticmethod
    def handler_of_method(method, chain):
        f2str = lambda f :f"{module_of_callable(f)}.{f.__name__}"
        return ff.find(chain.handlers, lambda h: f2str(h.method) == f2str(method) )

    def inspect(self, method: Callable, chain:taskflow.Chain, step: int) -> dict:
        handler = self.handler_of_method(method, chain)
        print ("called:", method)
        return dict(
            method_module = module_of_callable(method),
            method_name = method.__name__,
            method_doc = method.__doc__,
            handler_type = handler.__class__.__name__,
            handler_topic = handler.topic,
            order = step
        )


class ObserverMiddleware:
    def __init__(self, chain: taskflow.Chain) -> None:
        self.step = 1
    
    @abstractmethod
    def inspect(self, method: Callable, chain:taskflow.Chain, step: int) -> dict:
        pass

    def __call__(self, method, data, **kwargs):
        self.inspect(method, self.chain, self.step)
        self.log.info("\nSTEP #{} [{}], data after:\n {!r}".format(self.step, method.__name__, result))
        self.step += 1
        return data

if __name__ == "__main__":
    def task1(data):
        return data

    def task2(data):
        return data

    def task3(data):
        return data

    chain = taskflow.Chain("Main").then(task1).on("event", task2).then(task3)
    middleware = StateShapeExplorer(chain)
    result = chain({}, middleware=middleware)
    print(middleware.results)
