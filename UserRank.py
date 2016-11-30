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


class UserRank:
     
    def __init__(self):
        print ''
           
    """
    create_dictionary
    parameters: list of tweets
    returns: dictionary with key as the username who tweets and value as the list of users who are tweeted
    """
    def create_dictionary(self, lines):
        global_dict = {}
        
        for line in lines:
            try:
                tweet = simplejson.loads(line)
                #user = tweet['user']['screen_name'].encode('ascii', 'ignore').lower()
                user = tweet['user']['screen_name'].lower()
                user_mentions_list = tweet['entities']['user_mentions']
                
                user_mentions = []
                for dict in user_mentions_list:
                    #user_mentions.append(dict['screen_name'].encode('ascii', 'ignore').lower())
                    user_tobe_added = dict['screen_name'].lower()
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
                   
                    #empty_list = [] 
                    for user_mentioned in user_mentions:
                        if user_mentioned not in global_dict:
                            global_dict[user_mentioned] = []
                         
            except ValueError:
                pass
            
        return global_dict
    
    """
    dict_normalNodes_deadEndNodes
    parameters: dictionary with key as the username who tweets and value as the list of users who are tweeted
    returns: tuple with two values
        value1:  dictionary with key as the username who tweets and value as the list of users who are tweeted
                 However, here only those keys have been included whose value list is non-empty
        value2: dictionary with key as the username who tweets and value as the list of users who are tweeted.
                However, here only those keys have included whose value is an empty list
    """
    def dict_normalNodes_deadEndNodes(self, global_dict):
        dict_normalNodes = {}
        dict_deadendNodes = {}
        keys = global_dict.keys()
        
        for key in keys:
            if len(global_dict[key]) != 0:
                dict_normalNodes[key] = global_dict[key]
            else:
                dict_deadendNodes[key] = []
                
        return dict_normalNodes, dict_deadendNodes
    
                 
    """
    
    """            
    def map_userToId(self, normalNodes_deadendNodes_dict):
        list1 = sorted(normalNodes_deadendNodes_dict[0])
        map_normalNodes = {}
        value = 0
        for key in list1:
            map_normalNodes[key] = value
            value += 1
            
        list2 = sorted(normalNodes_deadendNodes_dict[1])
        map_deadendNodes = {}
        for key_dash in list2:
            map_deadendNodes[key_dash] = value
            value += 1
        
        return map_normalNodes, map_deadendNodes
    
    """
    map_IdToUser
    parameters: dictionary with key as the username and the value as the userID.
    returns: dictionary with key as the userID and value as the username
    """
    def map_IdToUser(self, userToIdMap):
        list1 = sorted(userToIdMap[0])
        dict = {}
        key = 0
        for val in list1:
            dict[key] = val
            key += 1
            
        list2 = sorted(userToIdMap[1])
        for val_dash in list2:
            dict[key] = val_dash
            key += 1
            
        return dict
    
    """
    create_sparse_matrix
    parameters: 
        1. dictionary with key as the username who tweets and value as the list of users who are tweeted
        2. dictionary with key as the username and value as the userID.
    returns: sparse matrix
    """
    def create_sparse_matrix(self, global_dict, userToIdMap):
        user_list = userToIdMap[0].keys()
        N = len(global_dict.keys())
        M = len(userToIdMap[0])
        sparse_matrix = scipy.sparse.lil_matrix((M,N))
        
        for user in user_list:
            user_mentions_list = global_dict[user]
            user_mentioned_count = float(len(user_mentions_list))
            for user_mentioned in user_mentions_list:
                #if user_mentioned_count != 0.0 and user_mentioned in global_dict:
                    #sparse_matrix[userID_dict[user], userID_dict[user_mentioned]] = 0.9*(1.0/user_mentioned_count) + 0.1*(1.0/float(N))
                if user_mentioned in userToIdMap[0]:
                    sparse_matrix[userToIdMap[0][user], userToIdMap[0][user_mentioned]] = 0.9*(1.0/user_mentioned_count)
                else:
                    sparse_matrix[userToIdMap[0][user], userToIdMap[1][user_mentioned]] = 0.9*(1.0/user_mentioned_count)
                    #matrix[userID_dict[user], userID_dict[user_mentioned]] = 0.9*(1.0/user_mentioned_count) + 0.1*(1.0/float(N))
                #else:
                    #matrix[userID_dict[user], userID_dict[user_mentioned]] = 0.0
        return sparse_matrix
        #return matrix
    
    """
    convergeToSteadyState
    parameters: 
        1. sparse matrix
        2. dictionary with key as the userName and value as user ID.
    returns: list containing the converging values corresponding to different users.
             Using this list we can conclude regarding the ranks of various users.
    """
    def convergeToSteadyState(self, sparse_matrix, userToIdMap):
        N = len(userToIdMap[0].keys()) + len(userToIdMap[1].keys())
        M = len(userToIdMap[0].keys())
        teleport_value = 0.1/float(N)
        teleport_value_dash = 1.0/float(N)
        val = 1.0/float(N)
        initial_vector = [val for x in range(M)]
        initial_vector_dash = [val for x in range(N-M)]
        final_vector_dash = [0 for x in range(N)]
        
        iteration = 0
        while True:
            start = time()
            
            common_factor = teleport_value * sum(initial_vector) + teleport_value_dash * sum(initial_vector_dash)
            final_vector = [common_factor for y in range(N)]
            
            nonzero_indices = nonzero(sparse_matrix)
            
            tuple_list = zip(nonzero_indices[0], nonzero_indices[1])
            sorted_tuple_list = sorted(tuple_list, key = lambda x: x[1])
            
            for tup in sorted_tuple_list:
                final_vector[tup[1]] += initial_vector[tup[0]] * sparse_matrix[tup[0], tup[1]]
                
            error = 0.0
            for n in range(N):
                error +=  abs(final_vector_dash[n] - final_vector[n])
                
            if error < 0.0005:
                break
            else:
                print error
                final_vector_dash = final_vector
               
            initial_vector = final_vector[:M]
            initial_vector_dash = final_vector[M:]
            
            iteration += 1
            #print final_vector
            print "time taken in iteration", iteration, time() - start
            
        return final_vector
    
    
    def main(self):
        if len(sys.argv) != 2:
            print "usage: ./UserRank.py <file to read json data(tweets)>"
            sys.exit(1) 
            
        filename = sys.argv[1]
        f = file(filename, "r")
        tweets = f.readlines()
        
        start = time()
        #userRank = UserRank()
        #dict_user_userMentions = create_dictionary(tweets)
        global_dict = self.create_dictionary(tweets)
        print "totol number of users:", len(global_dict.keys())
        normalNodes_deadendNodes_dict = self.dict_normalNodes_deadEndNodes(global_dict)
        print "time for creating dict_user_userMentions:", time() - start
        
        
        
        #print dict_user_userMentions
        
        start = time()
        #dict_userID =  createUserIdDictionary(dict_user_userMentions)
        userToIdMap = self.map_userToId(normalNodes_deadendNodes_dict)
        print "time for creating dict_userID: ", time() - start
        
        '''
        sys.stdout = open("C:\\test1\\2.txt", 'w')
        for key, value in dict_userID.items():
            print key, value
        '''
        
        #print dict_userID
        start = time()
        #id_user = id_user_map(dict_userID)
        idToUserMap = self.map_IdToUser(userToIdMap)
        
        print "time for creating id_user_map:", time() - start
        #print id_user
        
       
        start = time()
        sparse_matrix = self.create_sparse_matrix(global_dict, userToIdMap)
        print "time for creating sparse_matrix: ", time() - start
        
        #print sparse_matrix
        
        
        '''
        for index in range(len(dict_userID)):
            print sparse_matrix.getrow(index)
        '''
        
        #print sparse_matrix
        
        
        final_vector = self.convergeToSteadyState(sparse_matrix, userToIdMap)
        
        result_dict = {}
        for index in range(len(final_vector)):
            result_dict[final_vector[index]] = idToUserMap[index]
            
        '''
        indexes = [x for x in range(len(final_vector))]
        top50elements = nlargest(50, indexes, key=lambda i : final_vector[i])
        for elem in top50elements:
            print idToUserMap[elem]
        '''
        final_dict = {}    
        resulting_list = sorted(result_dict, reverse=True)
        for index in range(len(resulting_list)):
            final_dict[result_dict[resulting_list[index]]] = index + 1
            
        return final_dict
        
        
if __name__ == '__main__':
    
    userRank = UserRank()
    final_dict = userRank.main()
    
    #print final_dict['dirtysteeeve']
    
    '''
    resulting_list = sorted(result_dict, reverse=True)
    
    for index in range(50):
        print index, result_dict[resulting_list[index]]
    '''
    
    userRank_tuples = sorted(final_dict.items(), key=lambda x: x[1])
    for index in range(50):
        print userRank_tuples[index][1], userRank_tuples[index][0]
    
    
    
    
          
    
    
     
 
    
                
                
                
                
                
            
            
            
            
            
    