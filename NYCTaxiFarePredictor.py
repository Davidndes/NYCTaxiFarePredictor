#NYC Taxi Fare predictor

import duckdb
connection = duckdb.connect()

#datapull = duckdb.read_parquet("/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet")

# Gathering, cleaning and organizing the data 
datapull = connection.execute("DESCRIBE SELECT * FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet'")

dataInspection = connection.execute("""
    SELECT trip_distance, tpep_pickup_datetime, tpep_dropoff_datetime, fare_amount, Airport_fee, total_amount 
    FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet'
    LIMIT 10
""").fetchdf()

numberofRows = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet'").fetchone()

invalidDistances = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance <= 0").fetchone()

invalidPrices = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE fare_amount <= 0").fetchone()

overLap = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance <= 0 AND fare_amount <= 0").fetchall()

validTrips = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND fare_amount > 0").fetchone()

nullData = connection.execute("""SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE fare_amount IS NULL """).fetchall()

distanceBounds = connection.execute("""SELECT MAX(trip_distance), MIN(trip_distance), AVG(trip_distance) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND fare_amount > 0 """).fetchall()

tripsAbove100 = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 100 AND fare_amount > 0 """).fetchone()

tripsAbove50 = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 50 AND fare_amount > 0 ").fetchone()

fareBounds = connection.execute("SELECT MAX(fare_amount), MIN(fare_amount), AVG(fare_amount) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND fare_amount > 0").fetchone()

faresAbove500 = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND fare_amount > 500 ").fetchone()

faresAbove200 = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND fare_amount > 200 ").fetchone()

tripstoExclude = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 50 AND fare_amount > 200").fetchone()

tripstoInclude = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND trip_distance <= 50 AND fare_amount > 0 AND fare_amount <= 200").fetchone()

cleaned_trips = connection.execute("CREATE VIEW cleaned_trips AS SELECT * FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet' WHERE trip_distance > 0 AND trip_distance <= 50 AND fare_amount > 0 AND fare_amount <= 200").fetchone()

sizeCleanTrips = connection.execute(" SELECT COUNT(*) FROM cleaned_trips").fetchone()

newTable = connection.execute("""SELECT tpep_pickup_datetime, 
                              EXTRACT(HOUR FROM tpep_pickup_datetime) AS PickupHour, 
                              EXTRACT(YEAR FROM tpep_pickup_datetime) AS PickupYear,
                              EXTRACT(MONTH FROM tpep_pickup_datetime) AS PickupMonth,
                              EXTRACT(MINUTE FROM tpep_pickup_datetime) AS PickupMinute,
                              EXTRACT(DAY FROM tpep_pickup_datetime) AS PickupDay,
                              date_diff('second' , tpep_pickup_datetime, tpep_dropoff_datetime)/60 AS Duration_Minutes FROM cleaned_trips
                              LIMIT 10""").fetchdf()

zeroDuration = connection.execute("""SELECT COUNT(*) FROM cleaned_trips WHERE date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) <= 180""").fetchone()

# this creates a python variable but inside execute is what duckdb responds to 
new_cleaned_trips = connection.execute("""CREATE OR REPLACE VIEW new_cleaned_trips AS SELECT * FROM cleaned_trips WHERE date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime)/60 > 0 AND date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime)/60 <= 180 """)

numberofCleanedTrips = connection.execute("SELECT COUNT(*) FROM new_cleaned_trips").fetchone()

inputsTable = connection.execute("""SELECT fare_amount AS Fares,
                              trip_distance AS Distance, 
                              EXTRACT(HOUR FROM tpep_pickup_datetime) AS PickupHour, 
                              EXTRACT(DOW FROM tpep_pickup_datetime) AS PickupDay,
                              date_diff('second' , tpep_pickup_datetime, tpep_dropoff_datetime)/60 AS Duration_Minutes FROM new_cleaned_trips
                              LIMIT 10000""").fetchdf()

#print(inputsTable.to_string(index=False))

#print(inputsTable.shape)

#print(inputsTable.dtypes)

y = inputsTable["Fares"]

x = inputsTable[["Distance", "PickupHour", "PickupDay", "Duration_Minutes"]]

# The training portion of the algorithm 
from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)

# each of these inputrs have different numerical ranges so these need to be standardized. this is where you subtract the mean from the vlaue and divide by the standard deviation. this can be done automatically using standardscaler in sklearn 

from sklearn.preprocessing import StandardScaler

standardizer = StandardScaler()

Standardized_x_train = standardizer.fit_transform(x_train)
Standardized_x_test = standardizer.transform(x_test)

# turn the data into tensors

import torch

tensorXtrain = torch.tensor(Standardized_x_test, dtype = torch.float32)
tensorXtest = torch.tensor(Standardized_x_test, dtype = torch.float32)

tensorYtrain = torch.tensor(y_train.to_numpy(), dtype = torch.float32).reshape(-1,1)
tensorYtest = torch.tensor(y_test.to_numpy(), dtype = torch.float32).reshape(-1,1)

print(tensorXtest.shape)
print(tensorXtrain.shape)
print(tensorYtest.shape)
print(tensorYtrain.shape)