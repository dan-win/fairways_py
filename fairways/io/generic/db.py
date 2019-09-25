import os

import logging

log = logging.getLogger()

class DbDriver:
    """Base class for database driver
    
    Raises:
        NotImplementedError: [description]
        NotImplementedError: [description]
        NotImplementedError: [description]
    
    Returns:
        [type] -- [description]
    """
    default_conn_str = ""
    autoclose = False

    @property
    def db_name(self):
        return self.conn_str.split("/")[-1]
    
    def is_connected(self):
        raise NotImplementedError(f"Override is_connected for {self.__class__.__name__}")

    def __init__(self, env_varname):
        """Constructor
        
        Arguments:
            env_varname {str} -- Name of enviromnent variable which holds connection string (e.g.: "mysql://user@pass@host/db")
        """
        self.conn_str = os.environ.get(env_varname, self.default_conn_str)
        log.debug(f"Loading {self}...")
        self.engine = None

    def __str__(self):
        return f"Driver {self.__class__.__name__} | {self.conn_str}"

    # def fetch(self, sql):
    #     raise NotImplementedError()

    # def change(self, sql):
    #     raise NotImplementedError()

    def get_records(self, query_template, **params):
        """
        Return list of records. 
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        # Convert all iterables to lists to 
        query = query_template.format(**params).replace('\n', " ").replace("\"", "\'")
        # log.debug("SQL: {}".format(query))
        return self.fetch(query)

    def execute(self, query_template, **params):
        """
        Modify records in storage
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        query = query_template.format(**params)
        # log.debug("SQL: {}".format(query))
        return self.change(query)