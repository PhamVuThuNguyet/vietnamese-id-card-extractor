import datetime as dt

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, unique=True)
    image = Column(String, nullable=False)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    sex = Column(Integer, nullable=False)
    nationality = Column(String, nullable=False)
    poo = Column(String, nullable=False)
    por = Column(String, nullable=False)
    doe = Column(Date, nullable=False)
    created_on = Column(DateTime, default=dt.datetime.now)
    bookings = relationship('Booking')


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, unique=True)
    client_id = Column(String, ForeignKey('clients.id'), nullable=False)
    room = Column(String, nullable=False)
    time_in = Column(DateTime, nullable=False)
    time_out = Column(DateTime, nullable=False)
    created_on = Column(DateTime, default=dt.datetime.now)
