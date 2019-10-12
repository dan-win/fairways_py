import functools

def tentative(comment):
    "You should use this feature with care, it is subject to change in future"
    # @functools.wraps(f)
    def wrapper(f):
        f.__doc__ = f"* tentative *:\n{comment}\n{f.__doc__}"
        # f.__doc__ = f"*tentative*:\n{comment}\n{f.__doc__}"
        return f
    return wrapper

def stable(comment):
    """You should keep this feature consistent if furtehr releases, 
    it is intended to be the same,
    it could be used in production"""
    # @functools.wraps(f)
    def wrapper(f):
        f.__doc__ = f"* tentative *:\n{comment}\n{f.__doc__}"
        # f.__doc__ = f"*tentative*:\n{comment}\n{f.__doc__}"
        return f
    return wrapper