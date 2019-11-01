from fairways.io.generic import (DataDriver, UriConnMixin, FileConnMixin)

import logging

log = logging.getLogger()

class SynDataDriver(DataDriver):

    def _ensure_connection(self):
        if self.is_connected():
            return
        log.warning("Restoring DB connection: {}".format(self.db_name))
        self._connect()

    def _connect(self):
        raise NotImplementedError(f"Override _connect for {self.__class__.__name__}")

    def __del__(self):
        if self:
            self.close()

    def close(self):
        if self.is_connected():
            self.engine.close()
            self.engine = None

    def _setup_cursor(self, cursor):
        return cursor

    def fetch(self, sql):
        log.debug("MySql: SQL fetch: {}".format(sql))
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(sql)
                cursor = self._setup_cursor(cursor)
                return cursor.fetchall()
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if self.autoclose:
                self.close()

    def change(self, sql):
        try:
            self._ensure_connection()
            with self.engine.cursor() as cursor:
                cursor.execute(sql)
            self.engine.commit()
        except Exception as e:
            log.error("DB operation error: {} at {}; {}".format(e, self.db_name, sql))
            raise
        finally:
            if self.autoclose:
                self.close()

    # Inherited (note: sync method, acts as a proxy to coroutine):
    # def get_records(self, query_template, **params):

    # Inherited:
    # def execute(self, query_template, **params):
