import os
SKIP_EXT_DB_SERVERS = not bool(os.getenv('FWS_RUN_TEST_EXT', False))