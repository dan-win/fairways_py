import functools

def tentative(comment):
    # @functools.wraps(f)
    def wrapper(f):
        f.__doc__ = f"* tentative *:\n{comment}\n{f.__doc__}"
        # f.__doc__ = f"*tentative*:\n{comment}\n{f.__doc__}"
        return f
    return wrapper