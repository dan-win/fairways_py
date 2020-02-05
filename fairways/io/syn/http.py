# -*- coding: utf-8 -*-
"""HTTP driver.
Requires `Requests  <https://requests.readthedocs.io/en/master/>`_.
"""
import requests
from requests.auth import HTTPBasicAuth
import re
import json

from .base import (SynDataDriver, UriConnMixin)
from fairways.io.generic.net import HttpQueryParams

import urllib.parse

import logging
log = logging.getLogger(__name__)

class Http(SynDataDriver, UriConnMixin):
    """HTTP driver.
    This implementation targeted RESTful services with json response.
    Supports Basic Auth.
    
    :param env_varname: Name of enviromnent variable (or settings attribute) which holds host part of resource (e.g.: "http://user@pass@host:port")
    :type env_varname: str
    """

    autoclose = False

    def is_connected(self):
        """Connection status.
        For HTTP we always re-connect per each request
        
        :return: Always False
        :rtype: bool
        """
        return False
    
    def _connect(self):
        pass

    def _make_request(self, **params):
        # p = HttpQueryParams(**params)
        uri_parts = self.uri_parts
        root_url = f'{uri_parts.scheme}://{uri_parts.host}'
        if uri_parts.port:
            root_url = f'{root_url}:{uri_parts.port}'
        abs_url = urllib.parse.urljoin(root_url, params.pop("url"))

        log.debug('Abs url: %s', abs_url)

        handler = getattr(requests, params.pop("method"))

        # kwargs = {}
        # if p.body:
        #     kwargs["data"] = p.body
        # if p.headers:
        #     kwargs["headers"] = p.headers
        
        # check whether basic auth is necessary:
        user, password = self.uri_parts.user, self.uri_parts.password

        if user and password:
            params["auth"] = HTTPBasicAuth(user, password)

        log.debug("REQUEST PARAMS: %s, %s", abs_url, params)

        response = handler(abs_url, **params )
        response.raise_for_status()
        return response


    def get_records(self, _, **params):
        """
        Return list of records. 
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        response = self._make_request(**params)

        if params.get('stream') == True:
            buffer = []

            if response.encoding is None:
                response.encoding = 'utf-8'

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    buffer.append(line)
            serialized = ''.join(buffer)
            return json.loads(serialized)

        return response.json()

    def execute(self, url_template, **params):
        """
        Modify records in storage
        This method is common for sync and async implementations (in latter case it acts as a proxy for awaitable)
        """
        self._make_request(**params)