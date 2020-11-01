import numpy as np
from hmmlearn import hmm

#TODO: Will return saved model from file
def loadModel():
    network = hmm.GaussianHMM(n_components=3, covariance_type="full")
    network.startprob_ = np.array([0.6, 0.3, 0.1])
    network.transmat_ = np.array([[0.7, 0.2, 0.1],
                                [0.3, 0.5, 0.2],
                                [0.3, 0.3, 0.4]])
    network.means_ = np.array([[0.0, 0.0], [3.0, -3.0], [5.0, 10.0]])
    network.covars_ = np.tile(np.identity(2), (3, 1, 1))
    
    return network

#TODO: Defines network architecture and returns untrained movel
def createModel():
    network = hmm.GaussianHMM(n_components=10, covariance_type="full", n_iter=10)

    
    return network

#TODO: Trains model based on data in text file, may be database later
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
