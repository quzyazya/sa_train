import datetime
from typing import Optional, Annotated
from sqlalchemy import (TIMESTAMP,
                        Enum,
                        Table, 
                        Column, 
                        String, 
                        Integer, 
                        MetaData, 
                        ForeignKey, 
                        PrimaryKeyConstraint, 
                        text, 
                        CheckConstraint, 
                        Index)

from sqlalchemy.orm import Mapped, mapped_column, relationship
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

    # id: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[intpk] # = mapped_column() можем не указывать, тк нечего указывать, работать будет и без функции
    username: Mapped[str]

    resumes: Mapped[list['ResumesOrm']] = relationship(
        back_populates='worker'
    )

    resumes_parttime: Mapped[list['ResumesOrm']] = relationship(

        back_populates = 'worker',
        primaryjoin = 'and_(WorkersOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == "parttime")',
        order_by = 'ResumesOrm.id.desc()' 
    )    

class Workload(enum.Enum):

    parttime = 'parttime'
    fulltime = 'fulltime'


class ResumesOrm(Base):

    __tablename__ = 'resumes'

    # id: Mapped[int] = mapped_column(primary_key=True) - до intpk (ввода в работу Annotated)
    id: Mapped[intpk] 
    title: Mapped[str_256]
    compensation: Mapped[Optional[int]]    # зп может не быть - [int | None] = Optional[int] = mapped_column(nullable = True)
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

    worker = Mapped['WorkersOrm'] = relationship(
        back_populates = 'resumes' 
    ) 

    vacancies_replied: Mapped[list['VacanciesOrm']] = relationship(
        back_populates='resumes_replied',
        secondary='vacancies_replies'
    )

    repr_cols_num = 2
    repr_cols = ('created_at')

    __table_args__ = (
        Index('title_index', 'title'),
        CheckConstraint('compensation > 0', name = 'checl_compensation_positive')
    )     


class VacanciesOrm(Base):
    __tablename__ = 'vacancies'

    id: Mapped[intpk]
    title: Mapped[str_256]
    compensation: Mapped[Optional[int]]

    resumes_replied: Mapped[list['ResumesOrm']] = relationship(
        back_populates='vacancies_replied',
        secondary='vacancies_replies'
    )


class VacanciesRepliesOrm(Base):
    __tablename__ = 'vacancies_replies'

    resume_id: Mapped[int] = mapped_column(
        ForeignKey('resumes.id', ondelete='CASCADE'),
        primary_key=True
    )

    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey('vacancies.id', ondelete='CASCADE'),
        primary_key=True
    )

    cover_letter: Mapped[Optional[str]]


metadata_obj = MetaData()

# объявляем таблицу (не создаем, а объявляем!)
workers_table = Table(
    'workers',   # название таблицы
    metadata_obj, # передаем объект метаданных
    Column('id', Integer, primary_key=True),
    Column('username', String) 
)

resumes_table = Table(
    'resumes',
    metadata_obj,
    Column('id', Integer, primary_key = True),
    Column('title', String(256)),
    Column('compensation', Integer, nullable = True),
    Column('workload', Enum(Workload)),
    Column('worker_id', ForeignKey('workers.id', ondelete = 'CASCADE')),
    Column('created_at', TIMESTAMP, server_default = text("TIMEZONE('utc', now())")),
    Column('updated_at', TIMESTAMP, server_default = text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow)
)

vacamcies_table = Table(
    'vacancies',
    metadata_obj,
    Column('id', Integer, primary_key = True),
    Column('title', String),
    Column('compensation', Integer, nullable = True)
)

vacancies_replies_table = Table(
    'vacancies_replies',
    metadata_obj,
    Column('resume_id', ForeignKey('resume.id', ondelete = 'CASCADE'), primary_key = True),
    Column('vacancy_id', ForeignKey('vacancies.id', ondelete = 'CASCADE'), primary_key = True)
)


