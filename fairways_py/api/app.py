# -*- coding: utf-8 -*-
import os, sys
from dotenv import load_dotenv

import api

from api import dynload
from api import log
from api.conf import settings

from api.underscore import Underscore as _
from api.decorators.entrypoint import Channel

import sys
import argparse
import json

import logging

log = logging.getLogger(__name__)

class App:
    
    def start(self, settings):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--pool', type=str, default=None, help="Run selected pool only (where name of a pool is a module name where pool is defined)")
        parser.add_argument('-d', '--data', type=str, default=None, help="Initial data for a pool in json format (ignored if no --pool specified)")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-t', '--task', type=str, default=None, help="Run selected task only (ignored if no --pool specified)")
        group.add_argument('-e', '--entrypoint', type=str, default="test", choices=("cron", "amqp", "test", "cmd"), help="Selected entrypoint of a pool (ignored if no --pool specified)")
        # --dry-run option
        
        args = parser.parse_args()

        ctx = json.loads(args.data or "{}")

        if args.pool:
            poolname = args.pool
            taskname = args.task
            entrypoint = args.entrypoint

            dynload.import_module(poolname)
            log.info("Pool imported: %s", poolname)
            pool = sys.modules[poolname]

            if entrypoint:
                e = _.filter(Channel.items(), lambda r: r.channel_tag == entrypoint and r.module == poolname)
                # e = triggers.enum_module_triggers(poolname, tag=entrypoint)
                if e is None:
                    raise KeyError("Module {} has no entypoint with type {}".format(poolname, entrypoint))
                method = e["method_"]
            else:
                method = getattr(pool, taskname, None)
                if method is None:
                    raise KeyError("Module {} has no task {}".format(poolname, taskname))
            print("Running single task: '{}' from pool: '{}'".format(taskname, poolname))
            method(ctx)

        else:
            # Import all:
            imported_names = []
            for mod_qname in settings.INSTALLED_APPS:
                dynload.import_module(mod_qname)
                imported_names += [mod_qname]

            log.info("Pools imported: %s", imported_names)

            self.run(args)

    def run(self, args):
        """Batch runner, you could override this method
        
        Arguments:
            args {[argparse args]} -- [Arguments from cli]
        """
        entrypoint = args.entrypoint or "cli"

        entrypoints = _.filter(Channel.items(), lambda e: e.channel_tag == entrypoint)

        log.info(f"Running {len(entrypoints)} triggers")

        for handler in _.map(entrypoints, lambda e: e.handler):
            handler(ctx)
