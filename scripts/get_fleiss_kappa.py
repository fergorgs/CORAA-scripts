import statistics
import numpy


# This script was originaly created as part of the works on the creation of the CORAA dataset, 
# created to assist the training of portuguese automatic speech recognition tools

# This is my own implementation of the algorithm used to calculate
# Fleiss' Kappa, based on the infos avalible here: https://en.wikipedia.org/wiki/Fleiss%27_kappa
# In this implementation, I try to give error messeges a little more intuitive compared to the 
# avalible python libraries
# The results, when not identical, differ by an order of 10^(-18)

# As input, the script requires only a csv file with the columns indicating the avaluator's votes.
# The file may have other types of columns as when, but the user is required to provide a list
# of ids of the columns that represent the votes
input_file = './input.csv'
category_columns = [2, 3]


# my_fleiss_kappa
# Calculate a kappa value
# RECEIVES: a matrix, composed of the csv's columns that represent the votes
# RETURNS: the kappa value
def my_fleiss_kappa(matrix):

    # Checks and initial values----------------------------------
    # -----------------------------------------------------------

    # Check if matrix is valid
    if(len(matrix) == 0 or len(matrix[0]) == 0):
        print("ERROR: Matrix dimentions invalid")
        return

    # Get number of subjects, raters and categories
    nSubjects = len(matrix)         # N
    nRaters = 0                     # n
    nCategories = len(matrix[0])    # k

    for i in range(0, nCategories):
        nRaters += matrix[0][i]

    # Check if number of raters is consistent
    for i in range(0, nSubjects):

        raters = 0
        for j in range(0, nCategories):
            raters += matrix[i][j]
        
        if(raters != nRaters):
            raise RuntimeError("Number of raters must be constant for all subjects")

    # pj---------------------------------------------------------
    # -----------------------------------------------------------
    # pj, the proportion of all assignments which were to the j-th category
    pj = []

    # Calculating pj for each category
    for j in range(0, nCategories):

        sum = 0

        for i in range(0, nSubjects):
            sum += matrix[i][j]

        pj.append(sum / (nSubjects * nRaters))

    # Checking if everything went well
    if(numpy.sum(pj) != 1):
        raise RuntimeError("Sum of pj's returned \"" + str(numpy.sum(pj)) + "\" (must be exactly \"1\")")

    # pi---------------------------------------------------------
    # -----------------------------------------------------------
    # pi, the extent to which raters agree for the i-th subject
    pi = []

    for i in range(0, nSubjects):

        sum = 0

        for j in range(0, nCategories):
            sum += (matrix[i][j] * matrix[i][j])
        
        sum -= nRaters

        pi.append(sum / (nRaters * (nRaters - 1)))

    # P----------------------------------------------------------
    # -----------------------------------------------------------
    # P, the mean of pi's
    
    P = statistics.mean(pi)

    # Pe---------------------------------------------------------
    # -----------------------------------------------------------
    # Pe
    Pe = 0

    for i in range(0, len(pj)):
        Pe += (pj[i] * pj[i])

    # kappa------------------------------------------------------
    # -----------------------------------------------------------
    # kappa, the actual kappa value

    kappa = (P - Pe) / (1 - Pe)

    return kappa





# MAIN CODE------------------------------------------------------
# -----------------------------------------------------------
matrix = []
lines = []

# builds the input matrix from the provided csv file
with open(input_file, 'r') as f:
    lines = f.readlines()

    for line in lines:

        line = line.split(';')
        row = []
        for column in category_columns:
            row.append(int(line[column]))
        
        matrix.append(row)

f.close()



val = my_fleiss_kappa(matrix)

print('Own fleiss Kappa value is: ' + str(val))