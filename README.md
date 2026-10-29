# NYC Taxi Fare Predictor

This is my second machine learning project, building on what I learned from implementing a CNN for handwritten digit classification.

## First Pass — Initial Approach

For this second project, I'm going to use what I learned from the digit classifier to build a taxi fare prediction model for NYC taxis.

I will train the model on publicly available NYC taxi trip data, from which I expect it to learn certain patterns according to time of day, location in the city, distance, weather (if available), and time of year.

My initial thought is that distance will be the primary feature, since it has a relatively direct relationship with fare prices, while the other conditions will adjust the prediction. For example, a one-mile trip may typically cost around $15, but depending on traffic, time of day, or other conditions, the actual fare could differ in a nonlinear way.

I will compare the model's performance against a linear regression baseline and explore implementing the model's inference calculations in C++.

### Pseudocode and Open Questions

- Import data from a public source.
- Clean and organize the data using Python, NumPy, and pandas.
- Build a neural network using fully connected layers rather than convolutional layers.
- Train the model and compare its predictions against a linear regression baseline.

A few questions I had going into this:

In the digit classifier, the 60,000 images were eventually reduced to 10 output neurons, each corresponding to a digit. In this case, the outcome is continuous rather than discrete, so how does that change the output layer and loss function?

Would the model predict a specific price or use intervals? How would it distinguish between $10.53 and $10.54?

Would it make sense to have different neurons responsible for different fare ranges, such as $20, $30, and so on, before estimating a specific price within that range?

And without convolutional filters, how would the model learn useful relationships between the input features?

---

## Second Pass — Classification vs. Regression

With this project, we're moving from classification to regression, which changes the output layer and loss function but not the fundamental learning process.

The process is still:

**Inputs → Prediction → Calculate loss → Backpropagation → Update weights**

The convolutional filters in the digit classifier were useful because the model needed to recognize spatial patterns in images. For the taxi fare predictor, the inputs are numerical features rather than images, so I'm using fully connected layers instead.

The model takes the trip features, passes them through two hidden layers, and produces a prediction using one output neuron.

I initially thought that a regression model might need multiple output neurons representing different price ranges. However, since the goal is to predict a continuous numerical value, a single output neuron is sufficient.

The model can predict values such as $10.53 or $10.54 without assigning a separate neuron to each possible fare.

Another difference is the loss function. In the CNN, I used cross-entropy loss because the model was predicting one of ten discrete classes. For this regression problem, I'm using mean squared error (MSE), which measures the average squared difference between predicted and actual fares.

The closer the prediction is to the actual fare, the smaller the error. During training, the optimizer adjusts the weights to minimize this loss.

The final layer does not use ReLU or softmax. Instead, it produces an affine transformation of the previous hidden layer's outputs, allowing the network to return a continuous value.

The hidden layers are called hidden because they sit between the input and output layers. They learn intermediate representations of the input features that are useful for predicting the final fare.

---

## Third Pass — Data Preparation and Preliminary Results

When working with large public datasets, it's necessary to clean the data before training the model.

For this project, I used NYC taxi trip data and selected four input features:

- Trip distance
- Pickup hour
- Pickup day
- Trip duration

Although I initially considered including weather, location, and other conditions, I decided to start with these four features to keep the project manageable.

I also standardized the inputs using scikit-learn's `StandardScaler`.

Standardization applies:

```text
z = (x - mean) / scale
```

Where:

- `x` is the original feature value.
- `mean` is the mean of that feature in the training dataset.
- `scale` is the scale calculated by `StandardScaler`.
- `z` is the standardized feature.

This means that `z` represents how far above or below the mean a particular observation falls, measured relative to the feature's scale.

Since the network was trained on standardized inputs, any new observations must undergo the same transformation before being passed through the model.

### Preliminary Results

The project has already started to demonstrate that a relatively small neural network can outperform a linear regression baseline on the selected taxi-trip dataset.

| Model | Test MSE | Test RMSE |
|---|---:|---:|
| Linear Regression | 24.9231 | $4.99 |
| Neural Network | 19.6710 | $4.44 |

This represents approximately an **11% reduction in RMSE** compared with linear regression.

The neural network consists of three fully connected layers:

```text
Input (4) -> Hidden Layer (16) -> Hidden Layer (8) -> Output (1)
```

The first two layers use ReLU activation functions, while the final layer produces the predicted fare.

The model was trained in PyTorch using MSE loss and the Adam optimizer.

These are preliminary results, and I will confirm the final model's performance before completing the project.

---

## Fourth Pass — Implementing Inference in C++

After training the model in PyTorch, I wanted to better understand how the network actually produces a prediction and whether implementing these calculations directly in C++ could improve computational performance.

Rather than training another model in C++, I exported the weights and biases from the trained PyTorch model and used them to reproduce the forward pass.

The C++ implementation consists of functions to load the saved parameters, standardize the input features, perform matrix-vector multiplication, and apply ReLU.

Each layer takes the outputs from the previous layer, multiplies them by the corresponding weights, and adds the biases. ReLU is then applied after the first two layers, with the final layer returning a single fare prediction.

I also exported the means and scales from `StandardScaler` so that the C++ implementation could apply the same preprocessing as PyTorch.

### Comparing C++ and PyTorch Predictions

Before comparing computational performance, I needed to confirm that the C++ implementation was producing the same predictions as PyTorch.

To do this, I trained the model in Python, exported its parameters, and passed the same sample taxi trip through both implementations.

The sample input was:

- Distance: 5 miles
- Pickup hour: 14
- Pickup day: 2
- Duration: 20 minutes

The results were:

| Implementation | Predicted Fare |
|---|---:|
| PyTorch | $24.607271194458008 |
| C++ | $24.607270733841279 |

The absolute difference was calculated as:

```text
Absolute difference = abs(PyTorch prediction - C++ prediction)

Absolute difference = 0.0000004606
```

The two implementations produced nearly identical predictions, suggesting that the C++ forward pass is correctly reproducing the calculations performed by PyTorch.

The small difference may be explained by numerical precision. PyTorch uses 32-bit floating-point numbers by default, while my C++ implementation currently uses `double`, which generally provides 64-bit precision.

This is only an initial validation using one observation. I still need to compare predictions across a larger sample to determine the maximum difference between the implementations.

### Next Steps

The next stage of the project will focus on testing the reliability and computational performance of the C++ implementation.

I plan to compare inference times between C++ and PyTorch, investigate whether parallelizing the matrix-vector operations using OpenMP improves performance, and explore how using `float` versus `double` affects numerical accuracy and runtime.

I also want to examine where the model makes its largest prediction errors and whether those errors are concentrated among certain types of taxi trips.

These experiments should help me better understand both the predictive limitations of the model and the tradeoffs involved in implementing neural network inference at a lower level.