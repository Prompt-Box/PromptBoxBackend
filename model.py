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

    trainingSequences = []
    lengths = []

    sequenceNumber = 0
    for i in textData.readlines():
        trainingSequences.append([])

        words = i.split(" ")
        for j in words:
            trainingSequences[sequenceNumber].append(languageModel.index(j))

        lengths.append(len(words))
        sequenceNumber += 1

    #print(trainingSequences)

    trainingSequences = np.array(trainingSequences)
    trainingSequences = trainingSequences.reshape(-1, 1)

    network.fit(trainingSequences, lengths)

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
