import firebase_admin
import os
from firebase_admin import credentials, db as firebase_db
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Identity
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv


load_dotenv()
# --- Firebase Initialization ---
cred = credentials.Certificate("firebase_credentials.json")  # Your Firebase credentials JSON
firebase_admin.initialize_app(cred, {"firebase_URL": os.getenv("firebase_URL")})

# --- PostgreSQL Setup ---
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
Base = declarative_base()


# --- SQLAlchemy Models ---
class Bin(Base):
    __tablename__ = 'bins'
    bin_id = Column(String, primary_key=True)
    distance = Column(Float)
    temperature = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)


class BinHistory(Base):
    __tablename__ = 'bin_history'
    id = Column(Integer,Identity(start=1, increment=1), primary_key=True)
    bin_id = Column(String)
    distance = Column(Float)
    temperature = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


# --- Store Function ---
def store_bin_data(bin_id, distance, temperature, lat, lon, last_updated):
    session = Session()
    bin_record = session.query(Bin).filter_by(bin_id=bin_id).first()

    if bin_record:
        if (bin_record.distance != distance or
                bin_record.temperature != temperature or
                bin_record.lat != lat or
                bin_record.lon != lon):
            history = BinHistory(
                bin_id=bin_id,
                distance=bin_record.distance,
                temperature=bin_record.temperature,
                lat=bin_record.lat,
                lon=bin_record.lon,
                timestamp=datetime.utcnow()
            )
            session.add(history)

            bin_record.distance = distance
            bin_record.temperature = temperature
            bin_record.lat = lat
            bin_record.lon = lon
            bin_record.last_updated = last_updated
    else:
        new_bin = Bin(
            bin_id=bin_id,
            distance=distance,
            temperature=temperature,
            lat=lat,
            lon=lon,
            last_updated=last_updated
        )
        session.add(new_bin)

    session.commit()
    session.close()


# --- Firebase Callback ---
def firebase_listener(event):
    if event.path == "/":
        for bin_id, bin_data in event.data.items():
            store_bin_data(
                bin_id=bin_id,
                distance=bin_data.get("distance", 0),
                temperature=bin_data.get("temperature", 0),
                lat=bin_data.get("lat", 0),
                lon=bin_data.get("lon", 0),
                last_updated=bin_data.get("last_updated", "")
            )
    else:
        bin_id = event.path.strip("/").split("/")[0]
        ref = firebase_db.reference(f"/sensor_data/{bin_id}")
        bin_data = ref.get() or {}
        store_bin_data(
            bin_id=bin_id,
            distance=bin_data.get("distance", 0),
            temperature=bin_data.get("temperature", 0),
            lat=bin_data.get("lat", 0),
            lon=bin_data.get("lon", 0),
            last_updated=bin_data.get("last_updated", "")
        )


# --- Start Listener ---
def start_listener():
    ref = firebase_db.reference("/sensor_data")
    ref.listen(firebase_listener)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print(" Firebase listener started.")
    Thread(target=start_listener, daemon=True).start()

    # Keep script running
    while True:
        pass

