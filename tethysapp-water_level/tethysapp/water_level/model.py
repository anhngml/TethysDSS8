import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from .app import WaterLevel as app

Base = declarative_base()

db_posfix = 'primary_db_v2'


# SQLAlchemy ORM definition for the dams table
class Station(Base):
    """
    SQLAlchemy Station DB Model
    """
    __tablename__ = 'stations'

    # Columns
    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String)
    pred_model_url = Column(String)

    # Relationships
    hydrograph = relationship('Hydrograph', back_populates='station', uselist=False)


class Hydrograph(Base):
    """
    SQLAlchemy Hydrograph DB Model
    """
    __tablename__ = 'hydrographs'

    # Columns
    id = Column(Integer, primary_key=True)
    station_id = Column(ForeignKey('stations.id'))

    # Relationships
    station = relationship('Station', back_populates='hydrograph')
    points = relationship('HydrographPoint', back_populates='hydrograph')


class HydrographPoint(Base):
    """
    SQLAlchemy Hydrograph Point DB Model
    """
    __tablename__ = 'hydrograph_points'

    # Columns
    id = Column(Integer, primary_key=True)
    hydrograph_id = Column(ForeignKey('hydrographs.id'))
    time = Column(Integer)  #: hours
    level = Column(Float)  #: cfs
    level_pred = Column(ARRAY(Float))

    # Relationships
    hydrograph = relationship('Hydrograph', back_populates='points')


def add_new_station(uuid, lat, long, name, pred_model_url):
    """
    Persist new station.
    """
    # Create new Dam record
    new_station = Station(
        latitude=lat,
        longitude=long,
        name=name,
        uuid=uuid,
        pred_model_url=pred_model_url
    )

    # Get connection/session to database
    Session = app.get_persistent_store_database(db_posfix, as_sessionmaker=True)
    session = Session()

    # Add the new dam record to the session
    session.add(new_station)

    # Commit the session and close the connection
    session.commit()
    session.close()


def get_all_stations():
    """
    Get all persisted stations.
    """
    # Get connection/session to database
    Session = app.get_persistent_store_database(db_posfix, as_sessionmaker=True)
    session = Session()

    # Query for all station records
    stations = session.query(Station).all()
    session.close()

    return stations


def assign_hydrograph_to_station(station_id, hydrograph_vals):
    """
    Parse hydrograph file and add to database, assigning to appropriate station.
    """
    # Parse file
    hydro_points = []

    try:
        for line in hydrograph_vals:
            line = line.decode('utf-8')
            sline = line.split(',')

            try:
                time = int(sline[0])
                level = float(sline[1])
                hydro_points.append(HydrographPoint(time=time, level=level))
            except ValueError:
                continue

        if len(hydro_points) > 0:
            Session = app.get_persistent_store_database(db_posfix, as_sessionmaker=True)
            session = Session()

            # Get dam object
            station = session.query(Station).get(int(station_id))

            # Overwrite old hydrograph
            hydrograph = station.hydrograph

            # Create new hydrograph if not assigned already
            if not hydrograph:
                hydrograph = Hydrograph()
                station.hydrograph = hydrograph

            # Remove old points if any
            for hydro_point in hydrograph.points:
                session.delete(hydro_point)

            # Assign points to hydrograph
            hydrograph.points = hydro_points

            # Persist to database
            session.commit()
            session.close()

    except Exception as e:
        # Careful not to hide error. At the very least log it to the console
        print(e)
        return False

    return True


def get_hydrograph(station_id):
    """
    Get hydrograph id from dam id.
    """
    Session = app.get_persistent_store_database(db_posfix, as_sessionmaker=True)
    session = Session()

    # Query if hydrograph exists for dam
    hydrograph = session.query(Hydrograph).filter_by(station_id=station_id).first()
    session.close()

    if hydrograph:
        return hydrograph.id
    else:
        return None


def init_primary_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    # Create all the tables
    Base.metadata.create_all(engine)

    # Add data
    if first_time:
        # Make session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Initialize database with two stations
        station1 = Station(
            uuid="c47cf499-2a99-47dc-bb50-a2e93d1c0b36",
            latitude=9.529458206308968,
            longitude=106.18066449426,
            name="Trần Đề",
            pred_model_url="http://..."
        )

        station2 = Station(
            uuid="874fce78-a500-427d-a7b1-1eeefd0f14cd",
            latitude=9.035177968777248,
            longitude=105.42862386677358,
            name="Gành Hào",
            pred_model_url="http://..."
        )

        # Add the dams to the session, commit, and close
        session.add(station1)
        session.add(station2)
        session.commit()
        session.close()
