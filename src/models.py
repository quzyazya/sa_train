import datetime
from typing import Optional, Annotated
from sqlalchemy import Table, Column, String, Integer, MetaData, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base, str_256
import enum    # Enum (Перечисление) — это тип данных, который определяет набор именованных констант.

# mapped_column позволяет использовать типы без повторного указания типа данных внутри себя
# так, н-р, в Column мы бы прописывали тип заново внутри скобочек

# integer primary_key:
intpk = Annotated[int, mapped_column(primary_key = True)] # сможем переиспользовать этот тип
created_at = Annotated[datetime.datetime, mapped_column(server_default = text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, 
                       mapped_column(server_default = text("TIMEZONE('utc', now())"), onupdate = datetime.datetime.utcnow)]

class WorkersOrm(Base):

    __tablename__ = 'workers'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]    # = mapped_column() можем не указывать, тк нечего указывать, работать будет и без функции

class Workload(enum.Enum):

    parttime = 'parttime'
    fulltime = 'fulltime'

class ResumeOrm(Base):

    __tablename__ = 'resumes'

    # id: Mapped[int] = mapped_column(primary_key=True) - до intpk (ввода в работу Annotated)
    id: Mapped[intpk] 
    title: Mapped[str_256]
    salary: Mapped[Optional[int]]    # зп может не быть - [int | None] = Optional[int] = mapped_column(nullable = True)
    workload: Mapped[Workload]
    worker_id: Mapped[int] = mapped_column(ForeignKey('workers.id', ondelete = 'CASCADE'))  # либо ForeignKey(WorkersOrm.id)
                                                                                # удаляем резюме (обычно так не делают)
                                                                                # каскадное удаление (CASCADE)                                                                                              
                                                                                # удаляет работника только из таблицы workers
                                                                                # если удаляем резюме остальные сохраняются
                                                                                # работник тоже сохраняется
    created_at: Mapped[created_at] 
    # server_default = func.now() - время в данный момент по вашему часовому поясу 
    # text("TIMEZONE('utc', now())") - sql запрос "приведи к utc текущее время"
    # created_at: Mapped[datetime.datetime] = mapped_column(default = ...) - само приложение будет оправлять время, а не СУБД
    updated_at: Mapped[updated_at]   # если обновляем резюме, запиши время и передай его в БД
    # лучше использовать sql trigger для updated_at, тк работа через ORM может быть не так эффективна
    # если utcnow - будет обновляться всегда, если utcnow() - всегда будет одно и то же время 
    














metadata_obj = MetaData()

# объявляем таблицу (не создаем, а объявляем!)
workers_table = Table(
    'workers',   # название таблицы
    metadata_obj, # передаем объект метаданных
    Column('id', Integer, primary_key=True),
    Column('username', String) 
)



