# -*- coding: utf-8 -*-

import os

class DataStore:
    FILEEXT = "_"

    def __init__(self, mount_dir):
        self.mount_dir = mount_dir

    def _writedata(self, fpath, data):
        raise NotImplementedError()

    def _readdata(self, fpath):
        raise NotImplementedError()

    def _fmt_path(self, datakey):
        fname = '{}.{}'.format(datakey, self.FILEEXT)
        return os.path.join(self.mount_dir, fname)

    def push(self, datakey, data):
        fpath = self._fmt_path(datakey)
        self._writedata(fpath, data)

    def pull(self, datakey):
        fpath = self._fmt_path(datakey)
        return self._readdata(fpath)


class JsonStore(DataStore):
    """
    """
    FILEEXT = "json"

    def _writedata(self, fpath, data):
        with open(fpath, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, default=json_serial))

    def _readdata(self, fpath):
        with open(fpath, 'r') as f:
            s = f.read()
        return json.loads(s)

    def snapshot(self, fname):
        """
        Chainable wrapper for underscore "closure":)
        """
        fpath = self._fmt_path(datakey)
        def wrapper(data):
            with open(fpath, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False))
        return wrapper


class XmlOut(DataStore):
    """
    Write-only facility to export XML snapshots.
    """
    FILEEXT = "xml"


class BinStore(DataStore):
    """
    Pickle
    """

    FILEEXT = "pickle"

    def _writedata(self, fpath, data):
        with open(fpath, 'wb') as f:
            pickle.dump(data, f)

    def _readdata(self, fpath):
        with open(fpath, 'rb') as f:
            data = pickle.load(f)
        return data


class NullStore(DataStore):
    """
    Empty storage as a stub
    """

    def __init__(self):
        pass

    def push(self, datakey, data):
        # print("STEP {}".format(datakey), "RESULT: ", data)
        pass

    def pull(self, datakey):
        raise NotImplementedError("NullStore does not keep any data!")

