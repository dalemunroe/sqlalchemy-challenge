
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
        #f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value

@app.route("/api/v1.0/precipitation")
def precipitation():

    st_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    sel = [Measurement.date,
           func.sum(Measurement.prcp)]
    last_years_prcp_data = session.query(*sel).\
        filter(Measurement.date > st_query_date).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all() 
    session.close()      
    prcp_dict = {date: prcp for date, prcp in last_years_prcp_data}

    return jsonify(Last_years_prcp_data=prcp_dict)

# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():

    no_stations = session.query(Station.station).all()
    
    session.close()
    number_of_stations=list(np.ravel(no_stations))
    return jsonify(Number_of_stations=number_of_stations)


# Query the dates and temperature observations of the most active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def temp():
    st_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=364)
    mostact_station_tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > st_query_date).\
        filter(Measurement.station == "USC00519281").\
        order_by(Measurement.date).all()   
    session.close()
    station_tobs_data=list(np.ravel(mostact_station_tobs_data))
    
    return jsonify(Station_tobs_data=station_tobs_data)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.max(Measurement.tobs),
           func.min(Measurement.tobs),
           func.avg(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        tempstat_to_ds_end = session.query(*sel).\
            filter(Measurement.date >= start).all()
        session.close()
        tempstat_result=list(np.ravel(tempstat_to_ds_end))
        return jsonify(Temp_to_end = tempstat_result)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    tempstat_to_nom_end = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    tempstat_result_range=list(np.ravel(tempstat_to_nom_end))
    return jsonify(Temp_nom_range=tempstat_result_range)


if __name__ == '__main__':
    app.run()
