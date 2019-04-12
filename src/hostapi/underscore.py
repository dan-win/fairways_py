# -*- coding: utf-8 -*-
_methods = (
    'contains',
    'count_by', 
    'each', 
    'every', 
    'extend', 
    'find_where', 
    'find', 
    'flatten',
    'group_by', 
    'index_by', 
    'invoke', 
    'map', 
    'max', 
    'min', 
    'omit', 
    'partition', 
    'pick',
    'pluck', 
    'reduce_right', 
    'reduce', 
    'reject', 
    'sample', 
    'select',
    'shuffle', 
    'size', 
    'some', 
    'sort_by', 
    'where', 
    )

class Underscore(object):
    @staticmethod
    def uniq(iterable):
        if iterable is None: return None
        return list(set(list(iterable)))

    @staticmethod
    def filter(iterable, callable):
        if iterable is None: return None
        return [item for item in iterable if callable(item)]
    
    @staticmethod
    def reduce(iterable, callable, memo):
        for item in iterable:
            memo = callable(memo, item)
        return memo

    @staticmethod
    def extend(*args):
        args = list(args)
        dest = args.pop(0)
        for source in args:
            if source:
                dest.update(source)
        return dest

    @staticmethod
    def omit(data, *keys):
        if data is None: return None
        return {k: v for k, v in data.items() if k not in keys}

    @staticmethod
    def pick(data, *keys):
        if data is None: return None
        return {k: v for k, v in data.items() if k in keys}

    @staticmethod
    def contains(iterable, value):
        return value in iterable
    
    @staticmethod
    def count_by(iterable, callable):
        result = {}
        for item in iterable:
            key = callable(item)
            result[key] = result.get(key, 0) + 1
        return result

    @staticmethod
    def each(iterable, callable):
        iterator = iterable
        if isinstance(iterable, dict):
            for key, value in iterable.items():
                callable(value, key, iterable)
        else:
            for i, value in enumerate(iterable):
                callable(value, i, iterable)

    @staticmethod
    def every(iterable, callable):
        if iterable is None: return None
        return reduce(iterable, lambda v: bool(callable(v)), true)

    @staticmethod
    def find(iterable, callable):
        if iterable is None: return None
        for item in iterable:
            if callable(item):
                return item
        return None

    @staticmethod
    def find_where(iterable, properties):
        if iterable is None: return None
        result = []
        for item in iterable:
            flag = True
            for key, value in properties.items():
                if not item[key] == value:
                    flag = False
                    break
            if flag:
                # result.append(item)
                return item
        return None

    @staticmethod
    def map(iterable, callable):
        if iterable is None: return None
        return [callable(item) for item in iterable]

    @staticmethod
    def group_by(iterable, iteratee):
        if iterable is None: return None
        if isinstance(iteratee, str):
            attrname = iteratee
            method = lambda v: v[attrname]
        elif callable(iteratee):
            method = iteratee
        else:
            raise TypeError()
        
        def grouper(memo, v):
            key = method(v)
            return Underscore.extend(memo, {
                key: memo.get(key, []) + [v]
            })

        return Underscore.reduce(iterable, grouper, {})

    @staticmethod
    def index_by(iterable, iteratee):
        if iterable is None: return None
        if isinstance(iteratee, str):
            attrname = iteratee
            method = lambda v: v[attrname]
        elif callable(iteratee):
            method = iteratee
        else:
            raise TypeError()
        
        def grouper(memo, v):
            key = method(v)
            return Underscore.extend(memo, {
                key: v
            })

        return Underscore.reduce(iterable, grouper, {})

    @staticmethod
    def pluck(iterable, propname):
        return Underscore.uniq(Underscore.map(iterable, lambda v: v[propname]))
    
    @staticmethod
    def sort_by(iterable, callable):
        return sorted(iterable, key=callable)

    @staticmethod
    def chain(object):
        return Chain(object)


class Chain(object):
    def __init__(self, data):
        if data is None:
            raise TypeError('Cannot operate with NoneType!')
        self._data = data
    
    def _method(self, name):
        method = getattr(Underscore, name)
        def wrapper(*args, **kwargs):
            data = _align_type(self._data)
            self._data = method(data, *args, **kwargs)
            return self
        return wrapper

    
    def __getattribute__(self, name):
        if name in dir(Underscore):
            return self._method(name)
        return object.__getattribute__(self, name)
    
    def saveto(self, writer, slice=None):
        data = _align_type(self._data)
        if slice:
            if isinstance(data, dict):
                data = { k:v for (k, v) in data.items()[:slice] }
            else:
                data = list(data)[:slice]
        writer(data)
        return self
    
    @property
    def value(self):
        return _align_type(self._data)



def _align_type(data):
    if data is None:
        return data
    if isinstance(data, (int, bool, float, str, dict)):
        return data
    # if isinstance(data, dict):
    #     return dict(data)
    else:
        return list(data)


#################
# def dumpjson(fname):
#     fpath = os.path.join(dump_path, fname)
#     def writer(data):
#         with open(fpath, 'wb') as f:
#             f.write(json.dumps(data, ensure_ascii=False).encode('utf8'))
#     return writer
#################


if __name__ == '__main__':

    _ = Underscore

    data = [
        {'id': 11, 'data': 'test1', 'tag': 'a'},
        {'id': 12, 'data': 'test2', 'tag': 'a'},
        {'id': 13, 'data': 'test3', 'tag': 'b'},
        {'id': 14, 'data': 'test3', 'tag': 'b'},
        {'id': 15, 'data': 'test3', 'tag': 'c'},
        {'id': 16, 'data': 'test3', 'tag': 'f'},
    ]

    def dumper():
        def wrapper(data):
            print('DUMP:', data)
        return wrapper
    
    test = Chain(data).sort_by(lambda v: -v['id']).saveto(dumper()).value

    stooges = [{'name': 'moe', 'age': 40}, {'name': 'larry', 'age': 50}, {'name': 'curly', 'age': 60}]
    print('pluck: ', _.pluck(stooges, 'name'))

    print("=============")

    test = _.find_where(data, {
        'data': 'test3',
    })

    print("=============")
    print(test)
    print("=============")

    test = _.find_where(data, {
        'data': 'test3',
        'tag': 'f'
    })

    print("=============")
    print(test)
    print("=============")

    test = _.map(data, lambda d: "{}+{}".format(d['data'], d['tag']))

    print("=============")
    print(test)
    print("=============")


    # print(test)

