from .observer import ObserverMiddleware

import influxdb

from fairways.decorators import (connection, entrypoint, use)

from fairways.io.syn.influx import InfluxDb
from fairways.funcflow import FuncFlow as ff

import os

# # from fairways.conf import settings
# from fairways.decorators import use

# CONF_KEY = "FLOW_OBSERVER"

# DEFAULT_CONF = {

# }

# @use.config(CONF_KEY)
# def set_conf(logging_conf):
#     if not logging_conf:
#         logging_conf = DEFAULT_CONF
#     logging.config.dictConfig(logging_conf)


DB_ALIAS = "db_fwff"
os.environ[DB_ALIAS] = "influxdb://houston:houston@localhost:8086/fairways_flow"

@entrypoint.cmd(param="initdb")
def init_db():
    conn = InfluxDb(DB_ALIAS)
    # conn.execute("""CREATE DATABASE fairways_flow """)
    # conn.execute("""CREATE RETENTION POLICY "oneday" ON "fairways_flow" DURATION 1d REPLICATION 1;""")


class InfluxReflectorMiddleware(ObserverMiddleware):

    def send_events(self):
        # event = ff.map(
        #     self.stages_dict.values(), lambda stage: ff.pick(stage.as_dict(), "key", "method_module", "process_state", "order"))

        def stage_to_rec(stage):
            measurement = "taskflow"
            tag_key = stage.key#.replace(".", "-")
            tag_name = stage.method_name
            tag_module = stage.method_module#.replace(".", "-")
            field_state = stage.process_state
            return f""" {measurement},key="{tag_key}",module="{tag_module}",name="{tag_name}" state="{field_state}" """
        
        line_script = ff.chain(self.stages_dict.values()).map(stage_to_rec).apply("\n".join).value

        line_script = "INSERT INTO oneday\n" + line_script
        # line_script = []
        
        conn = InfluxDb(DB_ALIAS)
        conn.execute(line_script)

        print(">>>", line_script)
        print(80*"=")


if __name__ == "__main__":
    # How to run: python -m fairways.ci.influx_observer -e initdb

    from fairways.decorators.entrypoint import Cli

    Cli.run()