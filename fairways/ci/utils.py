
import io
import csv

import logging
log = logging.getLogger(__name__)

from fairways.decorators.apitag import tentative 

def csv2py(s, typecast_fields=None):
    """
    Convert tab-delimited text with headers row to list if dicts.
    Emulate DB response for query
    """
    f = io.StringIO(s)
    py_obj = list(csv.DictReader(f, dialect="excel-tab"))
    if isinstance(typecast_fields, dict):
        for rec in py_obj:
            for name, value in rec.items():
                rule = typecast_fields.get(name)
                if  callable(rule):
                    try:
                        rec[name] = rule(value)
                    except Exception as e:
                        log.error("Error in csv2py: %s, %s", e, rec)
    return py_obj

def trace_middleware_factory(log):
    return TraceMiddleware(log)

class TraceMiddleware:

    def __init__(self, log):
        self.step = 1
        self.log = log

    def __call__(self, method, data, **kwargs):
        result = method(data)
        self.log.info("\nSTEP #{} [{}], data after:\n {!r}".format(self.step, method.__name__, result))
        self.step += 1
        return result

@tentative
def render_diagram(chain):
    "Render Mermaid.js markdown for external dashbords like Grafana"
    class NodeInfo:
        last_node_id = 0

        def __init__(self, node):            
            self.__class__.last_node_id += 1
            self.id = f"ID{self.__class__.last_node_id}"
            self.label = node.name
            self.node_type = node.__class__.__name__
            method = node.method
            self.comments = method.__doc__
            tags = node.topic.split("/")
            self.topic_root = tags.pop(0)
            self.sub_topic = "/".join(tags)

        def render(self, prev_id, child_path=[]):
            from fairways.taskflow import Envelope
            # shape = "%s(%s)" % (self.id, self.label)
            # if self.topic_root == Envelope.DATA_ROOT:
            prefix = ""
            if self.sub_topic:
                parent_path = "/".join(child_path)
                if self.sub_topic!= parent_path:
                    if parent_path:
                        while not self.sub_topic.startswith(parent_path):
                            prefix = "\nend\n"
                            child_path.pop()
                            parent_path = "/".join(child_path)
                    prefix = "\nsubgraph \"ON %s\"\n" % self.sub_topic
                    child_path.append(self.sub_topic)
                    # return "%s -->|on \"%s\"|%s[%s]" % (prev_id, self.sub_topic, self.id, self.label), self.id, child_path
            else:
                if child_path:
                    prefix = ""
                    while child_path:
                        prefix += "\nend\n"
                        child_path.pop()

            if self.topic_root == Envelope.DATA_ROOT:
                return "%s%s --> %s[%s]" % (prefix, prev_id, self.id, self.label), self.id, child_path
            if self.topic_root == Envelope.FAILURE_ROOT:
                return "%s%s --> %s[/%s\]" % (prefix, prev_id, self.id, self.label), self.id, child_path

            # if self.topic_root == Envelope.FAILURE_ROOT:
            #     if self.sub_topic:
            #         return "%s -->|on \"%s\"|%s[/%s\]" % (prev_id, self.sub_topic, self.id, self.label), self.id
            #     return "%s --> %s[/%s\]" % (prev_id, self.id, self.label), self.id
            # else:
            #     if self.topic.startswith(Envelope.DATA_ROOT):
            #         shape = "-->|on %s|[%s]" % (self.topic, self.label)
            #     elif self.topic.startswith(Envelope.FAILURE_ROOT):
            #         shape = "-->|on %s|[/%s\]" % (self.topic, self.label)

            return "%s%s --> %s<%s>" % (prefix, prev_id, self.id, self.label), self.id, child_path

    trace = ['graph TD']
    prev_id = 'Start'
    child_path = []
    for node in chain.handlers:
        info = NodeInfo(node)
        element, prev_id, child_path = info.render(prev_id, child_path)
        trace.append(element)
    return "\n".join(trace)


def module_of_callable(c):
    """Find name of module where callable is defined
    
    Arguments:
        c {Callable} -- Callable to inspect
    
    Returns:
        str -- Module name (as for x.__module__ attribute)
    """
    # Ordinal function defined with def or lambda:
    if type(c).__name__ == 'function':
        return c.__module__
    # Some callable, probably it's a class with __call_ method, so define module of declaration rather than a module of instantiation:
    return c.__class__.__module__