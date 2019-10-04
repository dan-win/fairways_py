__all__ = [
    "dba", 
    "env", 
    "env_vars"
]

import os
import sys
import functools

from fairways.funcflow import FuncFlow as ff

from .connection import DefineConnections

from . import entrypoint

# from ..io import DbTaskSetManager
# dba = DbTaskSetManager.inject_dba_decorator

def env(**env_vector):
    """Decorator for task callable - inject environment into function args
    
    Keyword Arguments:
        env_vector {dict} -- Additional environment to pass into function as named argument "env")
    
    Returns:
        callable -- Wrapped node
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(context, **kwargs):
            env = kwargs.get('env', {})
            env.update(env_vector)
            kwargs.update({"env": env})
            return func(context, **kwargs)
        return wrapper
    return decorator

def env_vars(*env_vars):
    """Decorator for task callable - inject environment into function args from environment variables listed
    
    Keyword Arguments:
        env_vars {list} -- Names of Environment variables from os.environ to pass into function as named argument "env")
    
    Returns:
        callable -- Wrapped node
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(context, **kwargs):
            env_vector = ff.pick(os.environ, *env_vars)
            env = kwargs.get('env', {})
            env.update(env_vector)
            kwargs.update({"env": env})
            return func(context, **kwargs)
            # return func(context, env=env)
        return wrapper
    return decorator

def connection(arg_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(context, **kwargs):
            entity = DefineConnections.find_module_entity(func.__module__)
            kwargs.update({arg_name: entity.subject})
            return func(context, **kwargs)
        return wrapper
    return decorator


def config(config_key):
    def decorator(func):
        func = entrypoint.conf(config_key=config_key)(func)
        global_conf_module = sys.modules.get('fairways.conf')
        if global_conf_module: 
            settings = global_conf_module.settings
            if settings:
                sub_conf = getattr(settings, config_key)
                try:
                    func(sub_conf)
                except Exception as e:
                    log.error(f"Error during conf loading for {module_name}: {e!r}")
        return func
    return decorator
