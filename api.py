import datetime
from datetime import datetime
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from db import TPoint, Train, session_scope

app = FastAPI()


class Point(BaseModel):
    timestamp: datetime
    longitude: float
    latitude: float
    speed: float

class TrainDataPost(BaseModel):
    timestamp: datetime
    connection: str
    serviceLevel: str
    gpsStatus: str
    internet: str
    latitude: float
    longitude: float
    series: int
    speed: float
    trainType: str
    tzn: str


class TrainDataExport(BaseModel):
    tzn: str
    series: int
    trainType: str
    points: List[Point] = []

    @classmethod
    def from_train(cls, train: Train):
        return cls(
            tzn=train.tzn,
            trainType=train.trainType,
            series=train.series,
            points=[Point(**p.to_dict()) for p in train.points],
        )


@app.post("/traindata")
async def post_traindata(
    train: TrainDataPost
):
    with session_scope() as session:
        db_train = session.query(Train).filter(Train.tzn == train.tzn).first()
        if db_train is None:
            db_train = Train(trainType=train.trainType, tzn=train.tzn, series=train.series)
            session.add(db_train)

        data = TPoint(
            timestamp=train.timestamp,
            connection=train.connection,
            serviceLevel=train.serviceLevel,
            gpsStatus=train.gpsStatus,
            internet=train.internet,
            latitude=train.latitude,
            longitude=train.longitude,
            speed=train.speed,
        )
        db_train.points.append(data)
        session.add(data)
    return 200


@app.get("/traindata/{tzn}", response_model=TrainDataExport)
async def get_traindata(tzn: str):
    with session_scope() as session:
        a = (session.query(Train).filter(Train.tzn == tzn)).first()
        return TrainDataExport.from_train(a)
