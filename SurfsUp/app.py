# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()

# reflect an existing database into a new model
# reflect the tables
base.prepare(autoload_with=engine)
base.classes.keys()
# Save references to each table
measurement = base.classes.measurement
station = base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"

    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # query for the dates and temperature observations from the last year.
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()
    # Create a dictionary from the row data and append data for precipitation and temperature
    results

    weather_data = [
        {"date": result[0], "precipitation": result[1]}
        for result in results
    ]

    #return results for date and precipitation in json format
    return jsonify(weather_data)



@app.route("/api/v1.0/stations")
def stations():
 
   #query to identify each unique station id.

    result = session.query(station.station).all()
    station_list = list(np.ravel(result))
    #create a dictionary of station lists.
    station_dict = {'Station': station_list}
    
    # Create a dictionary from the row data and append to a list of all_passengers
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from the last year.
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    station_measurement_count = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active = station_measurement_count[0][0]
   
    results = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year).filter(measurement.station == most_active).all()
    # Create a dictionary from the row data and append data for precipitation and temperature
    tobs_data = [
        {"date": result[0], "temperature": result[1]}
        for result in results
    ]
    
    session.close()

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def start(start):
    #return a json list temperatures after the given start date <start>
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all() 
    
    start_data = [
        {"Minimum Temp": result[0], "Average Temp": result[1], "Maximum Temp": result[2]}
        for result in results
    ]
    session.close()
    return jsonify(start_data)


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    #return a json list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all() 
    date_range_data = [
        {"Minimum Temp": result[0], "Average Temp": result[1], "Maximum Temp": result[2]}
        for result in results
    ]
    session.close()
    return jsonify(date_range_data)


if __name__ == "__main__":
    app.run(debug=True)
