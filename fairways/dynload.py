import importlib

def import_module(mod_qname):
    tags = mod_qname.split('.')
    mod_name = tags.pop()
    package_name = ".".join(tags) or None
    try:
        importlib.import_module(mod_qname)
    except ModuleNotFoundError as e:
        print(f"..Dyn import ERROR {package_name}:{mod_name}; {e!r}")
        raise

