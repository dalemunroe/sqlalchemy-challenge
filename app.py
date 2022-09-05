

from os import stat
from sqlalchemy import distinct
import numpy as np
import pandas as pd
import datetime as dt


# Reflect Tables into SQLAlchemy ORM
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup

app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value

@app.route("/api/v1.0/precipitation")
def precipitation():

    st_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=364)

    sel = [Measurement.date,
           func.sum(Measurement.prcp)]
    last_years_data = session.query(*sel).\
        filter(Measurement.date > st_query_date).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()   
    prcp_dict = {date: prcp for date, prcp in last_years_data}

    return jsonify(prcp_dict)

# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():

    no_stations = session.query(Station.station).all()
    
    session.close()
    stations=list(np.ravel(no_stations))
    return jsonify(stations=stations)


# Query the dates and temperature observations of the most active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def temp():
    st_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=364)
    station_tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > st_query_date).\
        filter(Measurement.station == "USC00519281").\
        order_by(Measurement.date).all()   
    session.close()
    temps=list(np.ravel(station_tobs_data))
    return jsonify(temps)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    sel = [Measurement.tobs,
           func.max(Measurement.tobs),
           func.min(Measurement.tobs),
           func.avg(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        most_active = session.query(*sel).\
            filter(Measurement.date >= start).all()
        session.close()
        return jsonify(most_active)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    most_active = session.query(*sel).\
        filter(Measurement.date >= start and end).all()
    session.close()
    statss=list(np.ravel(stat))
    return jsonify(statss)

if __name__ == '__main__':
    app.run()
