# -*- coding: utf-8 -*-
import os, sys
from dotenv import load_dotenv

import fairways

from . import dynload
from fairways.log import init as init_log
from fairways.conf import settings

from fairways.funcflow import FuncFlow as ff
from fairways.decorators.entrypoint import QA, RegistryItem
from fairways.decorators.entities import Mark

import sys
import argparse
import json

import logging

init_log()

log = logging.getLogger(__name__)

class App:

    def __init__(self):
        self.settings = settings
    
    def start(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--pool', type=str, default=None, help="Run selected pool only (where name of a pool is a module name where pool is defined)")
        parser.add_argument('-d', '--data', type=str, default=None, help="Initial data for a pool in json format (ignored if no --pool specified)")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-t', '--task', type=str, default=None, help="Run selected task only (ignored if no --pool specified)")
        group.add_argument('-e', '--entrypoint', type=str, default="qa", choices=("cron", "amqp", "test", "cmd"), help="Selected entrypoint of a pool (ignored if no --pool specified)")
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
                e = ff.find(Mark.items(), lambda r: r.mark_name == entrypoint and r.module == poolname)
                # e = triggers.enum_module_triggers(poolname, tag=entrypoint)
                if e is None:
                    raise KeyError("Module {} has no entypoint with type {}".format(poolname, entrypoint))
                assert isinstance(e, RegistryItem)
                method = e.handler
            else:
                method = getattr(pool, taskname, None)
                if method is None:
                    raise KeyError("Module {} has no task {}".format(poolname, taskname))
            print("Running single task: '{}' from pool: '{}'".format(taskname, poolname))
            method(ctx)

        else:
            # Import all:
            imported_names = []
            for mod_qname in self.settings.INSTALLED_APPS:
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

        entrypoints = ff.filter(Mark.items(), lambda e: e.mark_name == entrypoint)

        log.info(f"Running {len(entrypoints)} triggers")

        for handler in ff.map(entrypoints, lambda e: e.handler):
            ctx = {}
            handler(ctx)
