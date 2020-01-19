# -*- coding: utf-8 -*-
"""CSV data files (read/write operations). 
[!] Needs testing for write operations
"""

import csv

from .base import (SynDataDriver, FileConnMixin)

class Csv(SynDataDriver, FileConnMixin):
    """CSV file driver.

    :param env_varname: Name of enviromnent variable (or settings attribute) which holds file path.
    :type env_varname: str
    """

    @property
    def file_name(self):
        return self.conn_str.split("/")[-1]
    
    def get_records(self, query_template, **params):
        """Fetch data from file.
        
        :param query_template: Dict of args for standard csv.dictReader
        :type query_template: Dict
        :return: Result 
        :rtype: List[Dict]
        """
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
            log.error("CSV read error: %r at %s", e, self.file_name)
            raise

    def execute(self, query_template, **params):
        """Save data to file ("w" mode, file will be rewritten).
        
        :param query_template: Dict of args for standard csv.dictWriter
        :type query_template: Dict

        \**params - keyword args, "data" attribute (required) should be list of dicts.
        :return: Result 
        :rtype: List[Dict]
        """
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
            with open(self.conn_str, "w") as csvfile:
                writer = csv.DictWriter(csvfile, **kwargs)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
        except Exception as e:
            log.error("CSV write error: %r at %s", e, self.file_name)
            raise


