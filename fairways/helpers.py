# -*- coding: utf-8 -*-
from .funcflow import FuncFlow as ff

def get_nested(d, path, delimiter="/"):
    """
    Address nested dicts via combined path
    """
    def item_by_tag(d, tags):
        # print(">>>>>>>>>>>>>> running nested", d, tags)
        t = tags[-1]
        child = d[t]
        if len(tags) == 1:
            return child
        return item_by_tag(child, tags[:-1])

    tags = path.split(delimiter)
    tags.reverse()
    # print(">>>>>>>>>>>>>> splitted", tags)
    return item_by_tag(d, tags)

def get_nested_default(d, path, delimiter="/", default=None):
    """
    Address nested dicts via combined path
    """
    def item_by_tag(d, tags):
        # print(">>>>>>>>>>>>>> running nested", d, tags)
        t = tags[-1]
        try:
            child = d[t]
        except:
            return default
        if len(tags) == 1:
            return child
        return item_by_tag(child, tags[:-1])

    tags = path.split(delimiter)
    tags.reverse()
    # print(">>>>>>>>>>>>>> splitted", tags)
    return item_by_tag(d, tags)

def get_parent(d, path, delimiter="/"):
    """
    Return last inner dict which contains adressed item
    """
    tags = path.split(delimiter)
    tags = tags[:-1]
    if not tags:
        return d
    return get_nested(d, delimiter.join(tags), delimiter)


def get_lastkey(path, delimiter="/"):
    """
    Return name of the rightmost fragment in path
    """
    return path.split(delimiter)[-1]

def rows2dict(r, key_attr=None, value_attr=None):
    """
    Convert list of dicts to the mapped dict {key_attr -> value_attr} for specified namets of key and value attributes
    """
    return ff.reduce(r, lambda memo, r: ff.extend(memo, {r[key_attr]: r[value_attr]}), {})


def ColoredFormatterFactory(**kwargs):
    format_template = kwargs.pop("format_template")
    from colorlog import ColoredFormatter
    print("^^^^^^^^^^^^^^^^^^^^^^ ColoredFormatterFactory", ColoredFormatter)
    return ColoredFormatter(format_template, **kwargs)