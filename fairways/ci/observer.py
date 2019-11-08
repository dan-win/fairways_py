from fairways import (taskflow, funcflow)
from abc import abstractmethod
from typing import Callable
from .utils import module_of_callable
from enum import Enum

ff = funcflow.FuncFlow

class DryRunMiddleware:

    def __init__(self, chain: taskflow.Chain) -> None:
        self.step = 1
        self.results = []
        self.chain = chain
        # print("1")


    @abstractmethod
    def inspect(self, method: Callable, chain:taskflow.Chain, step: int) -> None:
        pass


    def __call__(self, method, data, **kwargs):
        # print("2")
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

def f2str(f):
    return f"{module_of_callable(f)}.{f.__name__}"


class StateDef:
    def __init__(self, handler, method, order):
        self.key = f2str(method)
        self.order = order
        self.method_module = module_of_callable(method)
        self.method_name = method.__name__
        self.method_doc = method.__doc__
        self.handler_type = handler.__class__.__name__
        self.handler_topic = handler.topic,
        self.method_addr = method

        self.process_state = ProcessState.READY

    def as_dict(self):
        return ff.copy(self.__dict__)


class StateShapeExplorer(DryRunMiddleware):

    @staticmethod
    def handler_of_method(method, chain):
        return ff.find(chain.handlers, lambda h: f2str(h.method) == f2str(method) )

    def inspect(self, method: Callable, chain:taskflow.Chain, step: int) -> dict:
        handler = self.handler_of_method(method, chain)

        return StateDef(handler, method, step)


class ProcessState(Enum):
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

class ObserverMiddleware:
    def __init__(self, chain: taskflow.Chain) -> None:
        stages = list(StateShapeExplorer(chain).walk())
        self.stages_dict = ff.index_by(stages, lambda stage: stage.method_addr)
        self.reset()

    def stagedef_of_method(self, method):
        return self.stages_dict[method]

    def reset(self):
        ff.each(self.stages_dict.values(), set_state_closure(ProcessState.READY))
        self.send_events()

    @abstractmethod
    def send_events(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(ff.map(self.stages_dict.values(), lambda stage: ff.pick(stage.as_dict(), "key", "process_state", "order")))
        print(80*"=")

    def __call__(self, method, data, **kwargs):

        try:
            print("Running for method: ", method)
            stage = self.stagedef_of_method(method)
            stage_order = stage.order
            if stage_order == 0:
                self.reset()

            predecessors_chain = ff.chain(
                    self.stages_dict.values()
                ).filter(
                    lambda stage: stage.order < stage_order
                ).value

            ff.chain(predecessors_chain).filter(
                    lambda stage: stage.process_state == ProcessState.READY
                ).each(
                    set_state_closure(ProcessState.SKIPPED)
                )

            ff.chain(predecessors_chain).filter(
                    lambda stage: stage.process_state == ProcessState.RUNNING
                ).each(
                    set_state_closure(ProcessState.FAILURE)
                )

            stage.process_state = ProcessState.RUNNING
            self.send_events()

            data = method(data)
            
            # Exit
            stage.process_state = ProcessState.SUCCESS
            self.send_events()

            return data
        except Exception as e:
            print("EXCEPTION: ", e, "at method: ", method.__name__)
            raise


def set_state_closure(state):
    def wrapper(stage, index, collection):
        stage.process_state = state
        return stage
    return wrapper


