import itertools
from typing import Generator, Any
from pydantic import ValidationError #type: ignore
from sqlalchemy.orm.interfaces import Mapper
from sqlalchemy.engine import Connection
from sqlalchemy import create_engine, event, Table, Column, Integer, String,\
    DateTime, Numeric, Boolean, Float, BigInteger, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session as _Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.pool import QueuePool
from configs.provider import ConfigsProvider
from contextlib import contextmanager
from datasets.data import HistoryTradeJSON


configs = ConfigsProvider().load_system_settings()
Base:DeclarativeMeta = declarative_base()#type: ignore
engine = create_engine(
    url = configs.db_uri,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
)


class SingletonMeta(type):
    _instances:dict[type, Any] = {}

    def __call__(cls:'SingletonMeta', *args:tuple[Any], **kwargs:dict[str, Any]) -> 'SingletonMeta':
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance 
        return cls._instances[cls]


class BaseModel(Base):#type: ignore
    __abstract__ = True
    pk = Column(BigInteger, autoincrement=True, primary_key=True)
    timestamp = Column(DateTime, unique=True)
    instrument = Column(String) 
    timeframe = Column(String) 
    open = Column(Numeric(30, 10)) 
    close = Column(Numeric(30, 10)) 
    high = Column(Numeric(30, 10)) 
    low = Column(Numeric(30, 10)) 
    volume = Column(Numeric(30, 10)) 
    volume_usdt = Column(Numeric(30, 10))


class DynamicClassProvider(metaclass=SingletonMeta):
    def __init__(self):
        self.classes: dict[str, type[BaseModel]] = {}
        self._load_classes()

    def _load_classes(self) -> None:
        user_settings = ConfigsProvider().load_user_settings()
        instIds = set(user_settings.instIds)
        timeframes = set(user_settings.timeframes)
        for inst_id, timeframe in itertools.product(instIds, timeframes):
            class_name = f"{inst_id.upper()}_{timeframe.upper()}"
            table_name = f"{inst_id.upper()}_{timeframe.upper()}"
            class_ = type(class_name, (BaseModel,), {
                '__tablename__': table_name,
                '__table_args__': {'extend_existing': True}
            })
            self.classes[class_name] = class_
        Base.metadata.create_all(engine) #type: ignore 

    def get_class(self, inst_id: str, timeframe: str) -> type[BaseModel]|None:
        class_name = f"{inst_id.upper()}_{timeframe.upper()}"
        return self.classes.get(class_name)


class Orders(Base): #type: ignore
    __tablename__ = 'POSITIONS_AND_ORDERS'
    pk = Column(BigInteger, autoincrement=True, primary_key=True)
    order_id = Column(String, nullable=False)
    order_type = Column(String, nullable=False)
    instrument = Column(String, nullable=False)
    side_of_trade = Column(String, nullable=False)
    leverage = Column(Integer, nullable=False)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=True)
    status = Column(Boolean, nullable=False)
    price_of_conrats = Column(Float, nullable=False)
    number_of_conrats = Column(Float, nullable=False)
    money_in_deal = Column(Float, nullable=True)
    enter_price = Column(Float, nullable=True)
    order_volume = Column(Float, nullable=False)
    takeprofit_price = Column(Float, nullable=True)
    takeprofit_order_id = Column(String, nullable=True)
    takeprofit_order_volume = Column(Float, nullable=True)
    stoploss_price = Column(Float, nullable=False)
    stoploss_order_id = Column(String, nullable=False)
    stoploss_order_volume = Column(Float, nullable=False)
    risk_coefficient = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    fee = Column(Float, nullable=True)
    money_income = Column(Float, nullable=True)
    percent_money_income = Column(Float, nullable=True)
    history_of_trade = Column(JSON, nullable=True)


def create_all() -> sessionmaker:
    DynamicClassProvider()
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return SessionLocal

SessionLocal = create_all()

@contextmanager 
def get_session() -> Generator[_Session, None, None]:
    session:_Session = SessionLocal() 
    try: 
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception from e
    finally:
        session.close()

def validate_json_field(mapper:Mapper, connection:Connection, target:Orders) -> None:
    if target.history_of_trade:
        try:
            HistoryTradeJSON(**target.history_of_trade)
        except ValidationError as e:
            raise ValueError("Invalid JSON data in history_of_trade") from e

event.listen(Orders, 'before_insert', validate_json_field)
event.listen(Orders, 'before_update', validate_json_field)