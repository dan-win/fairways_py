# -*- coding: utf-8 -*-

import requests
import re

from .base import SynDataDriver
from fairways.io.generic.types import (HttpQueryParams)

import urllib.parse

import logging
log = logging.getLogger(__name__)

class Http(SynDataDriver):

    autoclose = False

    def is_connected(self):
        return False
    
    def _connect(self):
        pass

    def _make_request(self, **params):
        p = HttpQueryParams(**params)
        abs_url = urllib.parse.urljoin(self.conn_str, p.url)
        print(f'Abs url: {abs_url}')

        handler = getattr(requests, p.method)
        kwargs = {}
        if p.body:
            kwargs["data"] = p.body
        if p.headers:
            kwargs["headers"] = p.headers

        response = handler(abs_url, **kwargs )
        response.raise_for_status()
        return response


    def get_records(self, _, **params):
        """
        Return list of records. 
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        response = self._make_request(**params)
        return response.json()

    def execute(self, url_template, **params):
        """
        Modify records in storage
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        self._make_request(**params)