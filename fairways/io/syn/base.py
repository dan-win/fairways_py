from fairways.io.generic import (DataDriver, UriConnMixin, FileConnMixin)

from abc import abstractmethod

import logging
log = logging.getLogger()

class SynDataDriver(DataDriver):
    """Base class for sync drivers.

    :param env_varname: Name of enviromnent variable (or settings attribute) which holds connection string (e.g.: "mysql://user@pass@host/db")
    :type env_varname: str
    """

    def _ensure_connection(self):
        if self.is_connected():
            return
        log.warning("Connecting resource: {}".format(self.db_name))
        self._connect()

    @abstractmethod
    def _connect(self):
        "Should be overriden in descendants"
        raise NotImplementedError(f"Override _connect for {self.__class__.__name__}")

    def __del__(self):
        if self:
            self.close()

    def close(self):
        """Close connection if alive.
        """
        if self.is_connected():
            self.engine.close()
            self.engine = None

    def _setup_cursor(self, cursor):
        return cursor

    def fetch(self, query_script):
        """Fetch data from resource
        
        :param query_script: Script to fetch data (SQL for databases)
        :type query_script: Any
        :return: Result 
        :rtype: List[Any]
        """
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(query_script)
                cursor = self._setup_cursor(cursor)
                return cursor.fetchall()
        except Exception as e:
            log.error("Resource operation error: %r at %s; %s", e, self.db_name, query_script)
            raise
        finally:
            if self.autoclose:
                self.close()

    def change(self, query_script):
        """Change data on resource
        
        :param query_script: Script to fetch data (SQL for databases)
        :type query_script: Any
        """
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(query_script)
            self.engine.commit()
        except Exception as e:
            log.error("Resource operation error: %r at %s; %s", e, self.db_name, query_script)
            raise
        finally:
            if self.autoclose:
                self.close()

