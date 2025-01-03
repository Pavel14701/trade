from sqlalchemy.sql import exists
from sqlalchemy import event
from datetime import datetime
from typing import Any
from datasets.models import  DynamicClassProvider, Orders, get_session
from datasets.data import InstrumentTimeframeDataSchema, InstrumentTimeframeOrderData
from indicators.data import PriceData, PriceDataFrame


class PriceDbMethods:
    def dataframe_to_schema_list(self, df: PriceDataFrame, instId: str, timeframe: str) -> list[InstrumentTimeframeDataSchema]:
        data_list = [] 
        for _, row in df.iterrows():
            data = InstrumentTimeframeDataSchema(
                timestamp=row['date'],
                instrument=instId,
                timeframe=timeframe,
                open=row['open'],
                close=row['close'],
                high=row['high'],
                low=row['low'],
                volume=row['volume'],
                volume_usdt=row['volume_usdt'] 
            ) 
            data_list.append(data) 
        return data_list

    def add_data(self, instId:str, timeframe:str, data_list:list[InstrumentTimeframeDataSchema]) -> None:
        table_class = DynamicClassProvider().get_class(instId, timeframe)
        if table_class is None: 
            raise ValueError(f"No table found for {instId} and {timeframe}")
        with get_session() as session:
            for data in data_list:
                validated_data = data.model_dump()
                record = table_class(**validated_data) 
                session.add(record)

    def get_marketdata(self, instId:str, timeframe:str, _from:datetime|None=None, to:datetime|None=None) -> PriceDataFrame:
        table_class = DynamicClassProvider().get_class(instId, timeframe)
        if table_class is None:
            raise ValueError(f"No table found for {instId} and {timeframe}")
        with get_session() as session:
            query = session.query(
                table_class.timestamp, table_class.open, table_class.close,
                table_class.high, table_class.low, table_class.volume,
                table_class.volume_usdt
            )
            if _from:
                query = query.filter(table_class.timestamp >= _from)
            if to:
                query = query.filter(table_class.timestamp <= to)
            result: Any = query.order_by(table_class.timestamp).all()        
        data_dict = {
            'date': [row[0] for row in result],
            'open': [row[1] for row in result],
            'close': [row[2] for row in result],
            'high': [row[3] for row in result],
            'low': [row[4] for row in result],
            'volume': [row[5] for row in result],
            'volume_usdt': [row[6] for row in result]
        }
        price_data = PriceData(**data_dict)
        df = PriceDataFrame(price_data.model_dump())
        df.set_index('date', inplace=True)
        return df

    def save_new_order_data(self, data:InstrumentTimeframeOrderData) -> None:
        with get_session() as session:
            validated_data = data.model_dump()
            record = Orders(**validated_data)
            session.add(record)