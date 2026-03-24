import os
import sys
import asyncio
sys.path.insert(1, os.path.join(sys.path[0], '..'))


# from queries.core import create_tables, insert_data
from queries.core import AsyncCore, SyncCore
from queries.orm import SyncORM, AsyncORM

SyncORM.create_tables()
# SyncCore.create_tables()

SyncORM.insert_workers()
# SyncCore.insert_workers()

SyncCore.select_workers()

SyncCore.update_worker()