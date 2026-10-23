

#include <iostream>
#include <vector>
#include <fstream>

#include <sstream>
#include<string>


std::vector<double> neuronLayer(const std::vector<double>& newInputs,
              const std::vector<std::vector<double>>& LayerWeights,
              const std::vector<double> LayerBiases) {
              
              std::vector<double> Param = LayerBiases;
              for (int i = 0; i < LayerWeights.size(); i++)
                    for (int j = 0; j < newInputs.size(); j++)
                    Param[i] += LayerWeights[i][j] * newInputs[j];
              return Param;
            }

std::vector<double> relu(const std::vector<double>& inputs) {

    std::vector<double> Values(inputs.size());
    for (int i = 0; i < inputs.size(); i++)
        if (inputs[i] < 0) {
            Values[i] = 0;
        } else {
            Values[i] = inputs[i];
        };
    return Values;
}


std::vector<double> loadBiases(const std::string& filename) {

    std::ifstream file(filename);

    std::vector<double> biases;
    double value;

    while (file >> value) {
        biases.push_back(value);
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

