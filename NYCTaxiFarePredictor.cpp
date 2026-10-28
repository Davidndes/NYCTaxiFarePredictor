
#include <iostream> // this is to allow to the program to print to terminal using std::cout
#include <vector> // this allows you to access the specifci contianer std::vector in the cpp libarary which can chnage size dynamcially
#include <fstream> // this allows the program to read files using <ifstream> (read files?)
#include <sstream> // allows the program to treat strings as streams (a stream is an interface where data can be read or written)
#include <string> // allows the program to work with text
#include <iomanip> //this imports tools to use for manipulating how values are displayed 


// this first function acts as the code for a linear layer. it takes in inputs, weights and biases and constructs an output using them 
std::vector<double> neuronLayer(const std::vector<double>& scaledInputs, // this line starts the fucntion will std::datat_type function_name()
            const std::vector<std::vector<double>>& LayerWeights, // these next lines import the data and variables that the function will use or act on ie they are the parameters, & means receives a refernce to the orginal vector rather than making a new a copy 
            const std::vector<double>& LayerBiases) { //  "const" makes sure that the function does not change those input variables themselves.
            // notice that the code for the action itself exists inside {}
            std::vector<double> Param = LayerBiases; // creates a vector where std is the c++ namespace, :: tells the engine to search it, vector creates a vector and <double> is the vector data type 
              
              
                if (!LayerWeights.empty() && LayerWeights[0].size() == scaledInputs.size() && LayerWeights.size() == LayerBiases.size()) {
                    for (int i = 0; i < LayerWeights.size(); i++) // this starts a for loop iterating over i. i++ adds 1 each time, vector.size() takes the number of variables in the vector, and the condition is captured inside ;;
                        for (int j = 0; j < scaledInputs.size(); j++)
                            Param[i] += LayerWeights[i][j] * scaledInputs[j];
                } else { 
                std::cout << "matrix vector size mismatch\n";
                }
            
            return Param;
            }

std::vector<double> relu(const std::vector<double>& inputs) { // this is the ReLU function. the purpose is to take the inputs and floor them at zero

    std::vector<double> Values(inputs.size()); // initializes a vector "Values" of size "inputs.size" 
    for (int i = 0; i < inputs.size(); i++)
        if (inputs[i] < 0) { // notice the structure of the if statement - if (condition) {code to be executed} else {code to be executed}
            Values[i] = 0;
        } else {
            Values[i] = inputs[i];
        };
    return Values;
}

std::vector<double> standardize(const std::vector<double>& inputs, // function returning a vector of standardized features
            const std::vector<double>& means,
            const std::vector<double>& scales
        ){
            std::vector<double> scaledInputs(inputs.size());
                for (int i = 0; i < inputs.size(); i++)
                    scaledInputs[i] = (inputs[i] - means[i])/ scales[i];
            return scaledInputs; 

        } 

std::vector<double> loadSavedVector(const std::string& filename) { // creates a function to load the .csv file containing. the trained biases. 
// here std::string allows the function to take in a string as its input 
    std::ifstream file(filename); // ifstream allows the algorithm to read the given input file

    std::vector<double> SavedVector; // creates a vector called biases which is going to take in the numbers extracted from the file 
    double value; // creates a floating point number 

    while (file >> value) { // here file holds the data coming through the stream, they stream objects that manage access to the data. the while sttaement means keep reading the file until you cannot read anymore
        SavedVector.push_back(value); // push_back is this the syntax used to append the "value" to the vector "biases"
    } // note that ">>" extracts data from an input stream while "<<" sends data to an oupt stream like std::cout
    return SavedVector;
}

std::vector<std::vector<double>> loadSavedMatrix( const std::string& filename) { // once again creating a function to load the .csv file containign the vector pf weig\ht vectors 

    std::ifstream file(filename);
    std::vector<std::vector<double>> matrix; // creats an empty 2D vector 
    std::string line; // creates a string variable called line

    while (std::getline(file, line)) { // getline is a function that reads text from a stream untl it sees a delimiter then it makes a new line 
        std::stringstream rowStream(line); // std::stringstream reads from string in memory (ie the one stroed in line) 
        std::string cell; // string variable created 
        std::vector<double> row; // vector created

        while (std::getline(rowStream, cell, ',')) {// lets getline read until there is a comma before starting a new line 
            row.push_back(std::stod(cell));
        }
        matrix.push_back(row);
    }
    return matrix;
}

int main() { // code taht the algorithm eexcutes right away

    // loading relevant files 
  
    std::vector<std::vector<double>> weights = loadSavedMatrix("firstLayer_weight.csv");
    std::vector<double> biases = loadSavedVector("firstLayer_bias.csv");

    std::vector<std::vector<double>> weights2 = loadSavedMatrix("secondLayer_weight.csv");
    std::vector<double> biases2 = loadSavedVector("secondLayer_bias.csv");

    std::vector<std::vector<double>> weights3 = loadSavedMatrix("LastLayer_weight.csv");
    std::vector<double> biases3 = loadSavedVector("LastLayer_bias.csv");

    std::vector<double> means = loadSavedVector("standardizer_mean.csv");
    std::vector<double> scales = loadSavedVector("standardizer_scale.csv");

    std::vector<std::vector<double>> x_test = loadSavedMatrix("xtestvalues.csv");
    

     // neural network layers 


    std::vector<double> predictions;
    for (int i = 0; i < x_test.size(); i++) {
        std::vector<double> scaledInputs = standardize(x_test[i], means, scales);

        std::vector<double> output1 = neuronLayer(scaledInputs, weights, biases);
        output1 = relu(output1);

        std::vector<double> output2 = neuronLayer(output1, weights2, biases2);
        output2 = relu(output2);

        std::vector<double> finaloutput = neuronLayer(output2, weights3, biases3);

        predictions.push_back(finaloutput[0]);
        
        //std::cout << std::setprecision(17) << "prediction is  " << predictions[0] << std::endl; // std::setprecision(17) lets you print a specific amout of significant figures, 17 in this case
    
    }
    
   

    std::ofstream outputFile("cpp_predictions.csv"); // outputs the numbers to a csv file
         for (int i = 0; i < predictions.size(); i++) {
            outputFile << std::setprecision(17) << predictions[i] << "\n";
         }

         outputFile.close();
    std::vector<double> python_predictions = loadSavedVector("python_predictions.csv");
    std::vector<double> cpp_predictions = loadSavedVector("cpp_predictions.csv");

         if (cpp_predictions.size() == python_predictions.size()) {
            
            double maxDifference = 0.0;
            double totalDifference = 0.0;

            for (int i = 0; i < cpp_predictions.size(); i++){
                double difference = cpp_predictions[i] - python_predictions[i];

                totalDifference += std::abs(difference);

                maxDifference = std::max(maxDifference, std::abs(difference));
            }
            double absMean = totalDifference / cpp_predictions.size();

            std::cout << maxDifference << std::endl;

            std::cout << absMean << std::endl;
         }

         

    return 0;
}