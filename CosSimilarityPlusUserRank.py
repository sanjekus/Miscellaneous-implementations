import sys
import re
import simplejson
import difflib
import math
import numpy as np
import scipy.sparse
from scipy import *
from heapq import nlargest
from time import time, clock
from UserRank import *
from CosineSimilarity import *

class CosSimilarityPlusUserRank:
    
    def __init__(self):
        print ''
    
    """
    map_userIDtoName
    parameters: list of tweets
    returns: dictionary with key as userId and value as the screen name of the user
    """
    def map_userIDtoName(self, tweets):
        dict = {}
        for tweet in tweets:
            try:
                tweet = simplejson.loads(tweet)
                dict[tweet['id']] = tweet['user']['screen_name'].lower()
            except ValueError:
                pass
            
        return dict


if __name__ == '__main__': 
    
    if len(sys.argv) != 2:
        print "usage: ./CosSimilarityPlusUserRank.py <file to read json data(tweets)>"
        sys.exit(1)
        
    filename = sys.argv[1]
    f = file(filename, "r")
    tweets = f.readlines()
    
    cosineSimilarity = CosineSimilarity()
    userRank = UserRank()
    cosSimilarityPlusUserRank = CosSimilarityPlusUserRank()
    
    userIDtoName_map = cosSimilarityPlusUserRank.map_userIDtoName(tweets)
    userRank_dict = userRank.main()
    preProcessedValues = cosineSimilarity.main(False)
    
    while True:
        input_query = raw_input("Enter query: ")
        
        query_terms = cosineSimilarity.split_text(input_query)
        query_vector = cosineSimilarity.calculateTFIDFVectorofQueryTerm(query_terms, preProcessedValues[1], preProcessedValues[2])
        
        final_dict = cosineSimilarity.calc_TFIDFofDocs(query_terms, preProcessedValues[0], query_vector)
        
        cosSimPlusPageRank_dict = {}
        for key, value in final_dict.items():
            userName = userIDtoName_map[key]
            if userName in userRank_dict:
                cosSimPlusPageRank_dict[key] = value * (1.0/float(userRank_dict[userName]))
            else:
                cosSimPlusPageRank_dict[key] = 0.0
            
        final_list = sorted(cosSimPlusPageRank_dict.items(), key=lambda x: x[1], reverse=True)
        
        new_list = [x[0] for x in final_list]
        new_list_length = len(new_list)
        
        if new_list_length == 0:
            print "Sorry, no match :("
        elif new_list_length >= 50:
            for index in range(50):
                val = new_list[index]
                print index+1, new_list[index], preProcessedValues[3][val]
        else:
            for index in range(new_list_length):
                val = new_list[index]
                print index+1, new_list[index], preProcessedValues[3][val]
            

    
  
    
    