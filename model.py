import numpy as np
from hmmlearn import hmm
import pickle

#TODO: Will return saved model from file
def loadModel():

    with open("hmm.pkl", "rb") as file: 
        network = pickle.load(file)
    
    return network

#Defines network architecture and returns untrained movel
def createModel():
    network = hmm.GaussianHMM(n_components=50, covariance_type="full", n_iter=10)

    return network

#Trains model based on data in text file, may be database later
def trainModel(network, languageModel):
    textData = open("textData.txt", "rb")
    wordCount = 1

    trainingSequence = []

    for i in textData.readlines():
        words = i.split(" ")
        for j in words:
            trainingSequence.append(languageModel.index(j))

    #print(trainingSequence)

    trainingSequence = np.array(trainingSequence)
    trainingSequence = trainingSequence.reshape(-1, 1)

    network.fit(trainingSequence)

    with open("hmm.pkl", "wb") as file: 
        pickle.dump(network, file)

    return network

#Builds a language model for the HMM
def buildLanguageModelFromText():
    uniqueWords = []
    textData = open("textData.txt", "rb")
    wordCount = 1

    for i in textData.readlines():
        words = i.split(" ")
        for j in words:
            if(j not in uniqueWords):
                #If a new word isn't in the uniquewords dictionary, add it
                uniqueWords.append(j)
            else:
                continue

    return uniqueWords
