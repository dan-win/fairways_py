# -*- coding: utf-8 -*-

import csv

from .dbi import DbDriver

class Csv(DbDriver):

    @property
    def file_name(self):
        return self.conn_str.split("/")[-1]

    def __init__(self, env_varname='DB_CONN', default=None):
        self.conn_str = os.getenv(env_varname, default)
        self.engine = None
    
    def get_records(self, query_template, **params):
        try:
            kwargs = dict(query_template)
        except TypeError as e:
            log.error("Csv file source should has query defined as a dict of args for csv.dictReader")
            raise
        try:
            with open(self.conn_str) as csvfile:
                reader = csv.DictReader(csvfile, **kwargs)
                return(list(reader))
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.file_name))

    def execute(self, query_template, **params):
        try:
            kwargs = dict(query_template)
        except TypeError as e:
            log.error("Csv file destination should have query defined as a dict of args for csv.dictWriter")
            raise
        try:
            data = params["data"]
        except KeyError:
            log.error("Csv file: missed mandatory argument 'data' for writing")
            raise
        try:
            with open("in.csv", "w") as csvfile:
                writer = csv.DictWriter(csvfile, **kwargs)
                writer.writeheader()
                for row in data:
                    writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.file_name))


