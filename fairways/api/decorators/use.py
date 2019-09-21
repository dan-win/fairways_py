__all__ = [
    "dba", 
    "env", 
    "env_vars"
]

from api.io.sync import DbTaskSetManager
dba = DbTaskSetManager.inject_dba_decorator

def env(override=True, **env_vector):
    """Decorator for task callable - inject environment into function args
    
    Keyword Arguments:
        env_source {dict} -- Environment to pass into function as named argument "env" (default: {os.environ})
        override {dict} -- Additional properties to override (default: {None})
    
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
        env_source {dict} -- Environment to pass into function as named argument "env" (default: {os.environ})
        override {dict} -- Additional properties to override (default: {None})
    
    Returns:
        callable -- Wrapped node
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(context, **kwargs):
            env_vector = _.pick(os.environ, *env_vars)
            env = kwargs.get('env', {})
            env.update(env_vector)
            kwargs.update({"env": env})
            return func(context, **kwargs)
            # return func(context, env=env)
        return wrapper
    return decorator