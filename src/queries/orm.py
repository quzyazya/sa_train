from sqlalchemy import select, text, insert
from database import sync_engine, async_engine, session_factory, async_session_factory, Base
from models import metadata_obj, workers_table, WorkersOrm
import asyncio

def create_tables():
    Base.metadata.drop_all(sync_engine)
    async_engine.echo = True
    Base.metadata.create_all(sync_engine)
    sync_engine.echo = True

class SyncORM:

    @staticmethod
    def create_tables():
        Base.metadata.drop_all(sync_engine)
        async_engine.echo = True
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with session_factory() as session:
            worker_bobr = WorkersOrm(username = 'Bobr')
            worker_curva = WorkersOrm(username = 'Curva')
            session.add_all([worker_bobr, worker_curva])      # добавляем данные в сессию (это не значит, что данные сделали commit() или т.п.) 
                                        # unit of work - можем добавлять много объектов, а sqlalchemy определит
                                        # в каком порядке нужно добавить эти сущности (экземпляры классов) в БД
            # до commit все хранится только в оперативной памяти
            session.flush()  # flush отправляет запрос в базу данных
            # После flush каждый из работников получает первичный ключ id, который отдала БД
            session.commit()

    @staticmethod
    def select_workers():
        with session_factory() as session:
            # worker_id = 1
            # worker_jack = session.get(WorkersOrm, worker_id) or get(..., {'id': worker_od})
            query = select(WorkersOrm)  # SELECT * FROM workers
            result = session.execute(query)
            workers = result.all()
            print(f'workers')



    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Pepel"):
        with session_factory() as session:
            worker_bobr = session.get(WorkersOrm, worker_id)
            worker_bobr.username = new_username
            session.commit()

class AsyncORM:

    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_data():

        async with async_session_factory() as session:
            worker_bobr = WorkersOrm(username = 'Bobr')
            worker_curva = WorkersOrm(username = 'Curva')
            session.add_all([worker_bobr, worker_curva])     # не требуется await, тк add_all() никуда не отправляет данные
            await session.flush()
            await session.commit()
