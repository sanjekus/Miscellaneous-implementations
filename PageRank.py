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

class PageRank:
     
    def __init__(self):
        print ''
           
    """
    create_dictionary
    parameters: list of tweets
    returns: dictionary with key as the userID who tweets and value as the list of users who are tweeted
    """
    def create_dictionary(self, lines):
        global_dict = {}
        
        for line in lines:
            try:
                tweet = simplejson.loads(line)
                user = tweet['user']['id']
                user_mentions_list = tweet['entities']['user_mentions']
                
                user_mentions = []
                for dict in user_mentions_list:
                    user_tobe_added = dict['id']
                    if user_tobe_added != user:
                        user_mentions.append(user_tobe_added)
                 
                if len(user_mentions) != 0:   
                    value_global_dict = []
                    if user in global_dict:
                        value_global_dict = global_dict[user]
                        value_global_dict.extend(user_mentions)
                        global_dict[user] = list(set(value_global_dict))
                    else:
                        global_dict[user] = user_mentions
                    
                    for user_mentioned in user_mentions:
                        if user_mentioned not in global_dict:
                            global_dict[user_mentioned] = []
                         
            except ValueError:
                pass
            
        return global_dict
    
    def map_IDtoUsername(self, tweets):
        dict = {}
        
        for tweet in tweets:
            try:
                tweet = simplejson.loads(tweet)
                user_mentions_list = tweet['entities']['user_mentions']
                
                for user_mentioned in user_mentions_list:
                    if user_mentioned['id'] not in dict:
                        dict[user_mentioned['id']] = user_mentioned['screen_name']
                        
            except ValueError:
                pass
            
        return dict
                
                
    def update_dictionary(self, global_dict):
        old_dict = {}
        new_dict = {}
        length = len(global_dict)
        
        for key in global_dict:
            old_dict[key] = 1.0
            
        iteration = 0
        start = time()
        while True:
            flag = False
            
            for key in global_dict:
                new_dict[key] = 0.0
              
            for key in global_dict:
                adjacency_list = global_dict[key]
                
                for elem in adjacency_list:
                    if elem in new_dict:
                        new_dict[elem] += 0.9 * (float(old_dict[key])/float(len(adjacency_list)))
                    
            for key, value in new_dict.items():
                if len(global_dict[key]) != 0:
                    new_dict[key] =  value + 0.1/float(length)
                else:
                    new_dict[key] = value + 1.0/float(length)
                    
            for elem in old_dict:
                if abs(new_dict[elem] - old_dict[elem]) < 0.0001:
                    flag = True
                else:
                    old_dict = new_dict.copy()
                    flag = False
                    break
                
            if flag == True:
                break
        
            iteration += 1
        
            print 'iteration:', iteration
                
        print 'total time taken:', time() - start  
        return new_dict
            
            
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: ./PageRank.py <file to read json data(tweets)>"
        sys.exit(1)
        
    filename = sys.argv[1]
    f = file(filename, "r")
    tweets = f.readlines()
    
    pageRank = PageRank()
    global_dict = pageRank.create_dictionary(tweets)
    print 'total number of users:', len(global_dict)
    new_dict = pageRank.update_dictionary(global_dict)
    idToUserMap = pageRank.map_IDtoUsername(tweets)
    
    final_list = sorted(new_dict.items(), key=lambda x: x[1], reverse=True)
    
    final_list_dash = []
    for l in final_list:
        final_list_dash.append(l[0])
     
    '''   
    if 'biobio' in final_list_dash:
        print "yes it exists"
    '''
    
    for index in range(50):
        print index+1, final_list[index][0], final_list[index][1], idToUserMap[final_list[index][0]]
    
             
            
        
            
            
        
            
        
            
            
            