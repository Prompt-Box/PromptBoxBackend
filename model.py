import numpy as np
from hmmlearn import hmm
import pickle
import re

#Returns saved model from file
def loadModel():

    with open("hmm.pkl", "rb") as file: 
        network = pickle.load(file)
    
    return network

#Defines network architecture and returns untrained movel
def createModel():
    network = hmm.GaussianHMM(n_components=50, covariance_type="full", n_iter=5)
    network.monitor_
    return network

#Trains model based on data in text file, may be database later
def trainModel(network, languageModel, wordDictionary):
    textData = open("textData.txt", "rb")
    wordCount = 1

    trainingSequences = []
    lengths = []

    sequenceNumber = 0
    for i in textData.readlines():
        sequence = []

        words = str(i.lower())
        words = re.sub("[:;\"]", "", words)
        words = re.sub("[\(\)]", " ", words)
        words = re.sub("([\.!?,])", " \g<0>", words)

        words = words.split(" ")[1:]
        for j in words:
            sequence.append(wordDictionary[j])

        lengths.append(len(words))
        sequenceNumber += 1
        sequence = np.array(sequence)
        trainingSequences.append(sequence)

    print("Finished creating training sequence data")

    #TEMPORARY FOR RESTRICTING AMOUNT OF DATA TO TRAIN ON
    trainingSequences = trainingSequences[:100]
    lengths = lengths[:100]

    trainingSequences = np.concatenate(trainingSequences)
    trainingSequences = trainingSequences.reshape(-1, 1)

    print("Finished converting to numpy")
    #print(trainingSequences[-10:])
    print(trainingSequences.shape)

    network.fit(trainingSequences, lengths)

    with open("hmm.pkl", "wb") as file: 
        pickle.dump(network, file)

    return network

#Builds a language model for the HMM
def buildLanguageModelFromText():
    uniqueWords = []
    wordDictionary = {}
    textData = open("textData.txt", "rb")
    wordCount = 1

    for i in textData.readlines():
        words = str(i.lower())
        words = re.sub("[:;\"]", "", words)
        words = re.sub("[\(\)]", " ", words)
        words = re.sub("([\.!?,])", " \g<0>", words)

        words = words.split(" ")[1:]
        for j in words:
            try:
                exists = wordDictionary[j]
            except:
                #If a new word isn't in the uniquewords tracked, add it
                uniqueWords.append(j)
                wordDictionary[j] = len(uniqueWords) - 1

    print(uniqueWords[-10:])
    print("finished generating language model")
    return uniqueWords, wordDictionary
