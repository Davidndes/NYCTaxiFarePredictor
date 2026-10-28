#NYC Taxi Fare predictor

import duckdb
connection = duckdb.connect()

# Gathering, cleaning and organizing the data 
datapull = connection.execute("DESCRIBE SELECT * FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet'")
dataInspection = connection.execute("""
    SELECT trip_distance, tpep_pickup_datetime, tpep_dropoff_datetime, fare_amount, Airport_fee, total_amount 
    FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet'
    LIMIT 10
""").fetchdf()
numberofRows = connection.execute("SELECT COUNT(*) FROM '/Users/deslandes/Documents/MIT 6.00.1x/NYCTaxiFarePredictor/Data/jantripdata2025.parquet'").fetchone() # counts the amount of rows we are working with in the data in total 
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
                              USING SAMPLE 100000 ROWS""").fetchdf()


y = inputsTable["Fares"] # therefore y conatins the correct answers 

x = inputsTable[["Distance", "PickupHour", "PickupDay", "Duration_Minutes"]] # contians contins the parameters associated with that answer

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

tensorXtrain = torch.tensor(Standardized_x_train, dtype = torch.float32)
tensorXtest = torch.tensor(Standardized_x_test, dtype = torch.float32)

tensorYtrain = torch.tensor(y_train.to_numpy(), dtype = torch.float32).reshape(-1,1)
tensorYtest = torch.tensor(y_test.to_numpy(), dtype = torch.float32).reshape(-1,1)

# building the network layers 

class TaxiFareNeuralNetwork (torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.firstLayer = torch.nn.Linear(in_features = 4, out_features = 16)
        self.secondLayer = torch.nn.Linear(in_features = 16, out_features = 8)
        self.LastLayer = torch.nn.Linear(in_features = 8, out_features = 1)
        self.ReLU = torch.nn.ReLU()


    def forward(self, tensorXtrain):
        netWork = self.firstLayer(tensorXtrain)
        netWork = self.ReLU(netWork)
        netWork = self.secondLayer(netWork)
        netWork = self.ReLU(netWork)
        netWork = self.LastLayer(netWork)
        return netWork

    
model = TaxiFareNeuralNetwork()

lossFunction = torch.nn.MSELoss()

optimizer = torch.optim.Adam(model.parameters(), lr = 0.01)

#predictions = model(tensorXtrain[:5])

#print(predictions)
#print(predictions.shape)

def TrainingSequence(model, tensorXtrain, tensorYtrain, lossFunction, optimizer):
    for epoch in range(1,1001):

        optimizer.zero_grad()
        ForwardPass = model(tensorXtrain)
        modelLoss = lossFunction(ForwardPass, tensorYtrain)
        modelLoss.backward()
        optimizer.step()

    return model

#predictions = model(tensorXtrain[:5])

trainedModel = TrainingSequence(model, tensorXtrain, tensorYtrain, lossFunction, optimizer)

torch.save(model.state_dict(), "taxi_model.pth")

model.eval()

with torch.no_grad():
    testPredictions = model(tensorXtest)
    testLoss = lossFunction(testPredictions, tensorYtest)
    testRMSE = torch.sqrt(testLoss)

    print(f"testLoss is {testLoss.item():.4f}")

    print(f" test RMSE is {testRMSE.item():.2f}")

# Linear baseline to test again 

from sklearn.linear_model import LinearRegression 

from sklearn.metrics import mean_squared_error
import numpy as np

LinearBaseline = LinearRegression()
LinearBaseline.fit(Standardized_x_train, y_train)

BaselinePrediction = LinearBaseline.predict(Standardized_x_test)

BaselineMSE = mean_squared_error(y_test, BaselinePrediction)
BaselineRMSE = np.sqrt(BaselineMSE)

print(f"BaselineMSE {BaselineMSE:.4f}")
print(f"BaselineRMSE {BaselineRMSE:.2f}")


#save the model training weights and data 

for name, parameter in model.named_parameters():
    filename = name.replace(".", "_") + ".csv"
    np.savetxt(filename, parameter.detach().numpy(), delimiter=",")


np.savetxt("standardizer_mean.csv", standardizer.mean_, delimiter=",")
np.savetxt("standardizer_scale.csv", standardizer.scale_, delimiter=",")
np.savetxt("xtestvalues.csv", x_test, delimiter=",")


# for testing agaisnt c++



#raw_inputs = np.array([[5,14,2,20]]) # np.array here coverts a python list into an array. the double [[]] will create a matrix
#scaled_inputs = standardizer.transform(raw_inputs) # transofrm is a method belonging to the standradizer object 
#input_tensor = torch.tensor(scaled_inputs, dtype=torch.float32) #transforms the data into tensor (a collection of matrices)

model.eval()

with torch.no_grad(): # disables gradent tracking, while " with" is used to entyer a context where rules temporarily apply
    predictions = model(tensorXtest).numpy().flatten() # creates a one-dimensional numpy array(a vector) numpy takes it from a pytorch tensor to a numpy array and then flattens to one dimension

np.savetxt("python_predictions.csv", predictions, delimiter = ",")

#print("comparison prediction is:", prediction.item()) # .item() here is necessary becasue prediction is a tensor in this case