

%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
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
conn = engine.connect()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )



## Testing 
data_measure_df = pd.read_sql("SELECT * FROM Measurement", conn)
data_station_df = pd.read_sql("SELECT * FROM Station", conn)


## Testing Do I need this?
print(data_measure_df.head())
print(data_measure_df.shape)


## Testing  Do I need this?
print(data_station_df.head())
print(data_station_df.shape)


## Testing Do I need this?
combined_df = pd.merge(data_measure_df, data_station_df, on="station", how="inner")
combined_df.head()
print(combined_df.shape)


# reflect an existing database into a new model
Base = automap_base()


# reflect the tables
Base.prepare(engine, reflect=True)


# View all of the classes that automap found
inspector = inspect(engine)
inspector.get_table_names()


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)


## Testing Do I need this?
data_measure_df = engine.execute("SELECT * FROM Measurement")

for record in data_measure_df:
    print(record)


# Exploratory Precipitation Analysis
combined_df['date'].max()


# Find the most recent date in the data set.  Need to add f string
last_date = combined_df['date'].max()
print(combined_df['date'].max())


# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Starting from the most recent data point in the database. 
# Calculate the date one year from the last date in data set.
st_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=364)
print("Start query date:", st_query_date)
st_query_date
sel = [Measurement.date,
        func.sum(Measurement.prcp)]
last_years_data = session.query(*sel).\
    filter(Measurement.date > st_query_date).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()   # Sort the dataframe by date
last_years_data


# Save the query results as a Pandas DataFrame and set the index to the date column
query_df = pd.DataFrame(last_years_data, columns=['date', 'prcp'])
query_df.set_index('date', inplace=False)
query_df.head(20)


# Use Pandas Plotting with Matplotlib to plot the data - Still wrong
query_df.plot(x = "date", y = "prcp", legend = True, rot = 90)
plt.title(("Last Years Precipitation"), fontsize=15)
plt.xlabel("Date") 
plt.ylabel("Rainfall (mm)")
plt.show()


# Use Pandas to calcualte the summary statistics for the precipitation data
query_df['prcp'].describe()


# Exploratory Station Analysis
# Design a query to calculate the total number stations in the dataset
from sqlalchemy import distinct

no_stations = session.query(Station.station).\
        group_by(Station.station).all()
no_stations


from sqlalchemy import distinct
no_stations1 = session.query(func.count(distinct(Station.station)))
print(no_stations1.all())


# Design a query to find the most active stations (i.e. what stations with the most rows?)
# List the stations and the counts in descending order.

sel = [Measurement.station,
        func.count(Measurement.station)]
station_records = session.query(*sel).\
    group_by(Measurement.station).\
    order_by(Measurement.station).all()
station_records


## Not Ascending yet
#Max Record Variable
# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
sel = [Measurement.tobs, 
       func.max(Measurement.tobs), 
       func.min(Measurement.tobs), 
       func.avg(Measurement.tobs)]
most_active = session.query(*sel).\
    filter(Measurement.station == "USC00519281").all()
most_active


# Using the most active station id
# Query the last 12 months of temperature observation data for this station 
station_tobs_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > st_query_date).\
    filter(Measurement.station == "USC00519281").\
    order_by(Measurement.date).all()   # Sort the dataframe by date
station_tobs_data


# Save the query results as a Pandas DataFrame and set the index to the date column
tobs_query_df = pd.DataFrame(station_tobs_data, columns=['date', 'tobs'])
tobs_query_df.set_index('date', inplace=False)
tobs_query_df.head(20)


# And plot the results as a histogram
plt.hist(tobs_query_df['tobs'], bins=12)
plt.xlabel("Date")
plt.ylabel("Frequency")
plt.title("Annual Temperature Obs.   Station USC00519281", fontsize=15)
plt.show()


# Close session
# Close Session
session.close()