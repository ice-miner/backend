import datetime
from datetime import datetime
from typing import List
from typing import Optional
from fastapi import FastAPI, Header, Request, Response, status
from pydantic import BaseModel
try:
    from api.db import TPoint, Train, session_scope
except ModuleNotFoundError:
    from db import TPoint, Train, session_scope
from Crypto.PublicKey import RSA
from hashlib import sha512
from pathlib import Path
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


keys = []

key_path  = Path("./pub_keys")
for file in key_path.rglob("*.pem"):         #reads key files
    with file.open("r") as f:
        key = RSA.import_key(f.read())
        keys.append(key)

if keys == []:
    raise Exception("no keys found...")

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

class TrainsExport(BaseModel):
    tzn: str
    series: int
    trainType: str

class TrainsExportList(BaseModel):
    trains: List[TrainsExport] = []

    @classmethod
    def from_query(cls, query):
        trains = []
        for i in query:
            trains.append(TrainsExport(
                tzn=i.tzn,
                series=i.series,
                trainType=i.trainType
            ))
        return cls(trains=trains)

@app.post("/traindata")
async def post_traindata(
    response: Response,
    train: TrainDataPost,
    request: Request,
    signature: str = Header(None),
):
    hash = int.from_bytes(sha512(request._body).digest(), byteorder="big")
    for key in keys:
        hashFromSignature = pow(int(signature), key.e, key.n)
        if hash == hashFromSignature:  # does not protect from multiple same requests
            with session_scope() as session:
                db_train = session.query(Train).filter(Train.tzn == train.tzn).first()
                if db_train is None:
                    db_train = Train(
                        trainType=train.trainType, tzn=train.tzn, series=train.series
                    )
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
                response.status_code = status.HTTP_201_CREATED
            return 201
        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return 401


@app.get("/traindata/{tzn}", response_model=TrainDataExport)
async def get_traindata(tzn: str):
    with session_scope() as session:
        a = (session.query(Train).filter(Train.tzn == tzn)).first()
        return TrainDataExport.from_train(a)

# @app.get("/trains", response_model=TrainsExportList)
# async def get_trains():
#     with session_scope() as session:
#         q = session.query(Train).all()
#         return

