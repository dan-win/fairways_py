# -*- coding: utf-8 -*-

import os
import re

from .base import (SynDataDriver, UriConnMixin)
from influxdb import InfluxDBClient
from urllib.parse import parse_qs as _parse_qs

import logging
log = logging.getLogger(__name__)

RE_INSERT_SCRIPT_PATTERN = re.compile(r"^[\n\s]*insert into (?P<retention>[^\s]*)[\n\s]*", flags=re.IGNORECASE)
RE_SIMPLE_INSERT_SCRIPT_PATTERN = re.compile(r"^[\n\s]*insert ", flags=re.IGNORECASE)

class InfluxDb(SynDataDriver, UriConnMixin):

    default_conn_str = "influxdb://username:password@localhost:8086/databasename"
    autoclose = True

    def is_connected(self):
        return self.engine is not None
    
    @property
    def time_precision(self):
        if hasattr(self, '__t_precision'):
            return getattr(self, '__t_precision')
        parts = self.uri_parts
        precision = 'ms'
        params = parts.params 
        if params:
            params = _parse_qs(parts.params)
            # precision=[ns,u,ms,s,m,h]	
            precision = params.get('precision', 'ms')
        setattr(self, '__t_precision', precision)
        return precision

    def _connect(self):
        parts = self.uri_parts
        udp_port = 4444
        use_udp = bool(parts.scheme == "udp+influxdb")
        if use_udp:
            params = _parse_qs(parts.params)
            udp_port = int(para.get("udp_port"))
        engine = InfluxDBClient(
            host=parts.host, 
            port=parts.port, 
            username=parts.user, 
            password=parts.password, 
            database=parts.path, 
            use_udp=use_udp, 
            udp_port=udp_port)
        self.engine = engine

    def fetch(self, sql):
        params = {'db': self.uri_parts.path}
        try:
            self._ensure_connection()
            # return self.engine.query(sql, params=params, database=self.uri_parts.path, chunked=True, chunk_size=100)
            result = self.engine.query(sql, params=params, database=self.uri_parts.path)
            data = []
            for measurement_key, values in result.items():
                measurement_name = measurement_key[0]
                for rec in values:
                    rec.update({'measurement': measurement_name})
                    data.append(rec)
            return data
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if self.autoclose:
                self.close()
    
    def change(self, line_script):
        """Execute sql-like line protocol statement,
        e.g.: "INSERT treasures,captain_id=pirate_king value=2"
        Reference: https://docs.influxdata.com/influxdb/v1.6/write_protocols/line_protocol_reference/
        https://docs.influxdata.com/influxdb/v1.6/write_protocols/line_protocol_tutorial/
        
        Arguments:
            line_script {string} -- Script with inserted parameters
        """
        params = {
                'db': self.uri_parts.path,
                'precision': self.time_precision
            }
        retention_policy = None
        try:
            self._ensure_connection()
            match = RE_INSERT_SCRIPT_PATTERN.match(line_script)
            database_or_retention = None
            if match:
                m = match.group
                retention_policy = m('retention')
                if retention_policy:
                    params.update({'rp': retention_policy})

            line_script = re.sub(RE_INSERT_SCRIPT_PATTERN, '', line_script)
            line_script = re.sub(RE_SIMPLE_INSERT_SCRIPT_PATTERN, '', line_script)
            line_script = [row.strip() for row in line_script.split('\n')]
            line_script = [row for row in line_script if row]
            log.debug("line_script: %s", line_script)
            response = bool(self.engine.write(line_script, params=params, expected_response_code=204, protocol="line"))
            if not response:
                raise Exception("Error writing data to InfluxDB")
        except Exception as e:
            log.error("DB operation error: {} at {}".format(e, self.db_name))
            raise
        finally:
            if self.autoclose:
                self.close()

