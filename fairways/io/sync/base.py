from fairways.io.generic.db import DbDriver

import logging

log = logging.getLogger()

class SynDbDriver(DbDriver):

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

    def fetch(self,sql):
        try:
            self._ensure_connection()
            with self.engine.execute(sql) as cursor:
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
            self.engine.execute(sql)
            log.debug("EXECUTING...........")
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
