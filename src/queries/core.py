from sqlalchemy import Integer, and_, func, text, insert, select, update
from database import async_engine, sync_engine
from models import Workload, metadata_obj, workers_table, resumes_table
from sqlalchemy.orm import aliased

def get_123_sync():
    with sync_engine.connect() as conn:
        res = conn.execute(text("SELECT 1,2,3 union select 4,5,6"))
        print(f"{res.first()=}")

async def get_123_async():
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1,2,3 union select 4,5,6"))
        print(f"{res.first()=}")

class SyncCore:

    @staticmethod
    def create_tables():
        sync_engine.echo = False
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with sync_engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES
            #     ('Bobr'),
            #     ('Curva');"""
            stmt = insert(workers_table).values(         # запрос работает немного медленнее, зато эффективен для большого
                [                                        # количества данных, поиска ошибок и прочего 
                    {'username': 'Bobr'},
                    {'username': 'Curva'}
                ]
            )
            # conn.execute(text(stmt))  если через insert workers
            conn.execute(stmt)   # если через insert(workers_table)
            conn.commit()

    @staticmethod
    def select_workers():
        with sync_engine.connect() as conn:
            query = select(workers_table)           # верни нам табличку воркеров  SELECT * FROM workers
            result = conn.execute(query)
            workers = result.all()
            # workers = result.scalars().all()
            print(f'{workers}')

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = 'Ramphuzahmeddin'):
        with sync_engine.connect() as conn:
            # stmt = text('UPDATE workers SET username=:new_username WHERE id=:id')
            # stmt = stmt.bindparams(new_username=new_username, id = worker_id)
            stmt = (
                update(workers_table)
                .values(username = new_username)
                # .where(workers_table.c.id == worker_id)
                # .filter(workers_table.c.id == worker_id)
                .filter_by(id = worker_id)
            )
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def insert_resumes():
        with sync_engine.connect() as conn:

            resumes = [
                {"title": "Python Junior Developer", "compensation": 50000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Разработчик", "compensation": 150000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Data Engineer", "compensation": 250000, "workload": Workload.parttime, "worker_id": 2},
                {"title": "Data Scientist", "compensation": 300000, "workload": Workload.fulltime, "worker_id": 2},
            ]

            stmt = insert(resumes_table).values(resumes)
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def insert_additional_resumes():
        with sync_engine.connect() as conn:
            workers = [
                {'username': 'Roman'},
                {'username': 'Batman'},
                {'username': 'Lion'}
            ]

            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]

            insert_workers = insert(workers_table).values(workers)
            insert_resumes = insert(resumes_table).values(resumes)
            conn.execute(insert_workers)
            conn.execute(insert_resumes)
            conn.commit()

    
    @staticmethod
    def select_resumes_avg_compesation(like_langueage: str = 'Python'):
        """
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        having avg(compensation) > 70000
        """
        with sync_engine.connect() as conn:
            query = (
                select(
                    resumes_table.c.workload,
                    # 1 вариант использования cast
                    # cast(func.avg(ResumesOrm.compensation), Integer).label('avg_compensation'),
                    # 2 вариант использования cast (предпочтительный способ)
                    func.avg(resumes_table.c.compensation).cast(Integer).label('avg_compensation') 
                )
                .select_from(resumes_table)
                .filter(and_(
                    resumes_table.c.title.contains(like_langueage),
                    resumes_table.c.compensation > 40000,
                ))
                .group_by(resumes_table.c.workload)
                .having(func.avg(resumes_table.c.compensation) > 70000)
            )
            print(query.compile(compile_kwargs = {'literal_binds': True}))
            res = conn.execute(query)
            result = res.all()
            print(result[0].avg_compensation)

    @staticmethod
    def join_cte_subquary__window_func():
        """
        WITH helper2 AS (
            SELECT *, compensation.avg_workload_compensation AS compensation_diff
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
            FROM rewsumes r
            JOIN workers w ON r.worker_id = w.id) helper1
            )    
        )
        SELECT * FROM helper2
        ORDER BY compensation_diff DESC;
        """
        with sync_engine.connect() as conn:
            r = aliased(resumes_table)
            w = aliased(workers_table)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.c.compensation).over(partition_by=r.c.workload).cast(Integer).label('avg_workload_compensation')
                )
                # .select_from(r)
                .join(r, r.c.worker_id == w.c.id).subquery('helper1')
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label('compensation_diff')
                )
                .cte('helper2')
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )

            res = conn.execute(query)
            result = res.all()
            print(f'{len(result)=}. {result=}')

    # Relationships отсутсвуют при использовании Table


            

class AsyncCore():
    # Асинхронный вариант
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata_obj.drop_all)
            await conn.run_sync(metadata_obj.create_all)

    @staticmethod
    async def insert_workers():
        async with async_engine.connect() as conn:
            
            stmt = insert(workers_table).values(
                [
                    {'username': 'Bobr'},
                    {'username': 'Curva'}
                ]
            )

            await conn.execute()
            await conn.commit()

    @staticmethod
    async def select_workers():
        async with async_engine.connect() as conn:
            query = select(workers_table) # SELECT * FROM workers
            result = await conn.execute(query)
            workers = result.all()
            print(f'{workers=}')

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = 'Misha'):
        async with async_engine.connect() as conn:
            # stmt = text('UPDATE workers SET username=:username WHERE id=:id')
            # stmt = stmt.bindparams(username=new_username, id=worker_id)
            stmt = (
                update(workers_table)
                .values(username=new_username)
                # .where(workers_table.c.id==worker_id)
                .filter_by(id=worker_id)
            )
            await conn.execute(stmt)
            await conn.commit()

    @staticmethod
    async def insert_resumes():
        async with async_engine.connect() as conn:
            resumes = [
                {'title': 'Python Junior Developer', 'compensation': 50000, 'workload': Workload.fulltime, 'worker_id': 1},
                {"title": "Python Разработчик", "compensation": 150000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Data Engineer", "compensation": 250000, "workload": Workload.parttime, "worker_id": 2},
                {"title": "Data Scientist", "compensation": 300000, "workload": Workload.fulltime, "worker_id": 2},
            ]

            stmt = insert(resumes_table).values(resumes)
            await conn.execute(stmt)
            await conn.commit

    @staticmethod
    async def select_resumes_avg_compensation(like_language: str = 'Python'):
        """
        select workload, avg(compensation):: int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        having avg(compensation) > 70000
        """ 
        async with async_engine.connect() as conn:
            query = (
                select(
                    resumes_table.c.workload,
                    # 1 вариант использования cast
                    # cast(func.avg(ResumesOrm.compensation), Integer).label('avg_compensation'),
                    # 2 вариант использования cast (предпочтительный способ)
                    func.avg(resumes_table.c.compensation).cast(Integer).label('avg_compensation')
                )
                .select_from(resumes_table)
                .filter(and_(
                    resumes_table.c.title.contains(like_language),
                    resumes_table.c.compansation > 40000
                ))
                .group_by(resumes_table.c.workload)
                .having(func.avg(resumes_table.c.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={'literal_binds': True}))
            res = await conn.execute(query)
            result = res.all()
            print(result[0].avg_compensation)

    @staticmethod
    async def insert_additional_resumes():
        async with async_engine.connect() as conn:
            workers = [
                {'username': 'Roman'},
                {'username': 'Batman'},
                {'username': 'Lion'}
            ]
            resumes = [
                {'title': 'Python программист', 'compensation': 60000, 'workload': 'fulltime', 'worker_id': 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(workers_table).values(workers)
            insert_resumes = insert(resumes_table).values(resumes)
            await conn.execute(insert_workers)
            await conn.execute(insert_resumes)
            await conn.commit()

    @staticmethod
    async def join_cte_subquery_window_func():
        """
        WITH helper2 AS (
            SELECT *, compensation-avg_workload_compensation AS compensation_diff
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload):: int AS avg_workload_compensation
            FROM resumes r
            JOIN workers w ON r.worker_id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER BY compensation_diff DESC;
        """
        async with async_engine.connect() as conn:
            r = aliased(resumes_table)
            w = aliased(workers_table)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.c.compensation).over(partition_by=r.c.workload).cast(Integer).label('avg_workload_compensation')
                )
                # .select_from(r)
                .join(r, r.c.worker_id == w.c.id).subquery('helper1')
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label('compensation_diff')
                )
                .cte('helper2')
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )

            res = await conn.execute(query)
            result = res.all()
            print(f'{len(result)=}. {result=}')

        # Relationships отсутствуют при использовании Table
