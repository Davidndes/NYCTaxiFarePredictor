
#include <iostream> // this is to allow to the program to print to terminal using std::cout
#include <vector> // this allows you to create vectors and arrays using std::<vector>
#include <fstream> // this allows the program to read files using <ifstream> (read files?)

#include <sstream> // allows the program to treat strings as streams (what does that mean?)
#include<string> // allows the program to work with text


// this first function acts as the code for a linear layer. it takes in inputs, weights and biases and constructs an output using them 
std::vector<double> neuronLayer(const std::vector<double>& newInputs, // this line starts the fucntion will std::datat_type function_name(). imports the 
              const std::vector<std::vector<double>>& LayerWeights, // these next lines import the data and variables that the function will use or act on.
              const std::vector<double> LayerBiases) { //  "const" makes sure that the function does not change those input variables themselves.
              // notice that the code for the action itself exists inside {}
              std::vector<double> Param = LayerBiases; // creates a vector where std is the c++ library, :: tells the engine to search it, vector creates a vector and <double> is the vector data type 
              for (int i = 0; i < LayerWeights.size(); i++) // this starts a for loop iterating over i. i++ adds 1 each time, vector.size() takes the number of variables in i, and the condition is captured inside ;;
                    for (int j = 0; j < newInputs.size(); j++)
                    Param[i] += LayerWeights[i][j] * newInputs[j];
              return Param;
            }

std::vector<double> relu(const std::vector<double>& inputs) { // this is the ReLU function. the purpose is to take the inputs and floor them at zero

    std::vector<double> Values(inputs.size());
    for (int i = 0; i < inputs.size(); i++)
        if (inputs[i] < 0) { // notice the structure of the if statement - if (condition) {code to be executed} else {code to be executed}
            Values[i] = 0;
        } else {
            Values[i] = inputs[i];
        };
    return Values;
}


std::vector<double> loadBiases(const std::string& filename) { // creates a function to load the .csv file containing. the trained biases. 
// here std::string allows the function to take in a string as its input 
    std::ifstream file(filename); // ifstream allows the algorithm to read the given input file

    std::vector<double> biases; // creates a vector called biases which is going to take in the numbers extracted from the file 
    double value;

    while (file >> value) {
        biases.push_back(value); // push.back is this the syntax used to append the "value" to the vector "biases"
    }

    return biases;
}

std::vector<std::vector<double>> loadWeights( const std::string& filename) {

    std::ifstream file(filename);

    std::vector<std::vector<double>> weights;
    std::string line;

    while (std::getline(file, line)) {
        std::stringstream rowStream(line);
        std::string cell;
        std::vector<double> row;

        while (std::getline(rowStream, cell, ',')) {
            row.push_back(std::stod(cell));
        }
        weights.push_back(row);
    }

    return weights;

}

int main() {

  
    std::vector<std::vector<double>> weights = loadWeights("firstLayer_weight.csv");
    std::vector<double> biases = loadBiases("firstLayer_bias.csv");

    std::vector<std::vector<double>> weights2 = loadWeights("secondLayer_weight.csv");
    std::vector<double> biases2 = loadBiases("secondLayer_bias.csv");

    std::vector<std::vector<double>> weights3 = loadWeights("LastLayer_weight.csv");
    std::vector<double> biases3 = loadBiases("LastLayer_bias.csv");

    std::vector<double> inputs = {-1,2,-3,4};
    
    std::vector<double> output1 = neuronLayer(inputs, weights, biases);
    output1 = relu(output1);

    std::vector<double> output2 = neuronLayer(output1, weights2, biases2);
    output2 = relu(output2);

    std::vector<double> finaloutput = neuronLayer(output2, weights3, biases3);
    
    std::vector<std::vector<double>> LayerWeights = {
        {1,2,3,4 ,5},
        {1,2,3,4 ,5},
        {1,2,3,4 ,5}
    };
    std::vector<double> LayerBiases = {3,2,10};
    std::vector<double> newInputs = relu(inputs);
    
    std::vector<double> NNOutput = neuronLayer(newInputs, LayerWeights, LayerBiases);

    std::cout << finaloutput[0] << std::endl;

        return 0;
}