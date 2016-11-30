# @author: Sanjeev Kumar Singh(UIN: 922002623)
# Created as part of Assignment-2 of Information Retrieval course(CSCE-670)

import sys
import re
import simplejson
import difflib
import math
import numpy
from time import time, clock


class CosineSimilarity:
    
    def __init__(self):
        print ''
        
    """
    split_text
    parameters: string
    returns: list of tokens    
    """
    def split_text(self, text):
        text = re.compile("[^\w]|_").sub(" ", text)
        word_list = re.findall("\w+", text.lower())    
        return word_list
    
    """
    create_dict
    parameters: list of tweets
    returns: dictionary with key as the term and value as the dictionary with key as the tweetID and
             value as the logarithmic term frequency.
    """     
    def create_dict(self, lines):
        dict = {}
        
        for line in lines:
            try:
                tweet = simplejson.loads(unicode(line),encoding="UTF-8")
                text = tweet['text'].lower()
                terms = self.split_text(text)
                set_terms = set(terms)
                
                for term in set_terms:
                    count = 0
                    for word in terms:
                        if term == word:
                            count += 1 
                    
                    docID = tweet['id']
                    temp_dict = {}
                    if term in dict:
                        temp_dict = dict[term]
                        
                    temp_dict[docID] = 1.0 + math.log(count, 2)
                    dict[term] = temp_dict
                  
            except ValueError:
                pass
                        
        return dict
    
    """
    updateDictWithIDF
    parameters: 
        1. dictionary with key as the term and value as the dictionary with key as the tweetID and
           value as the logarithmic term frequency.
        2. total number of tweets in the entire corpus
    returns: dictionary with key as the term and value as the dictionary with key as the tweetID and
             value as the product of logarithmic tf and idf
    """
    def updateDictWithIDF(self, dict, corpus_length):
        terms = dict.keys()
    
        for term in terms:
            temp_dict = dict[term]
            docIDList = temp_dict.keys()
            calculated_idf = math.log(float(corpus_length)/float(len(docIDList)), 2)
            
            for docID in docIDList:
                temp_dict[docID] *= calculated_idf
                
            dict[term] = temp_dict
            
        return dict
    
    """
    calculateNormalizationFactorForEachDoc
    parameters: dictionary with key as the term and value as the dictionary with key as the tweetID and
             value as the product of logarithmic tf and idf
    returns: dictionary with key as the docID and normalization factor or Euclidian distance for that doc
    """
    def calculateNormalizationFactorForEachDoc(self, dict):
        terms = dict.keys()
        dictionary = {}
        
        for term in terms:
            temp_dict = dict[term]
            docIDList = temp_dict.keys()
            
            for docID in docIDList:
                if docID in dictionary:
                    dictionary[docID] += temp_dict[docID] * temp_dict[docID]
                else:
                    dictionary[docID] = temp_dict[docID] * temp_dict[docID]
                    
        for key, value in dictionary.items():
            dictionary[key] = math.sqrt(value)
            
        return dictionary 
    
    """
    updateDictWithDocNormFactor
    parameters: 
        1. dictionary with key as the term and value as the dictionary with key as the tweetID and
        value as the product of logarithmic tf and idf
        2. dictionary with key as the docID and normalization factor or Euclidian distance for that doc
    returns:dictionary with key as the term and value as the dictionary with key as the tweetID and
             value as the normalized tf-idf
    """
    def updateDictWithDocNormFactor(self, dict, normalized_dict):
        terms = dict.keys()
        
        for term in terms:
            temp_dict = dict[term]
            docIDList = temp_dict.keys()
            
            for docID in docIDList:
                if normalized_dict[docID] != 0.0:
                    temp_dict[docID] = float(temp_dict[docID])/float(normalized_dict[docID])
                else:
                    temp_dict[docID] = 0.0
                
            dict[term] = temp_dict
            
        return dict
    
    """
    calculateTFIDFVectorofQueryTerm
    parameters: 
        1. tokens/terms of query
        2. dictionary with key as the term and value as the dictionary with key as the tweetID and
           value as the logarithmic term frequency.
        3. total number of tweets
    returns: list containing normalized tf-idf of terms of query
    """
    def calculateTFIDFVectorofQueryTerm(self, query_terms, dict_corpus, corpus_length):
        set_terms = set(query_terms)
        query_vector = []
        
        for term in set_terms:
            if term not in dict_corpus:
                continue
            else:
                count = 0
                for q_term in query_terms:
                    if term == q_term:
                        count += 1
                      
                tf_factor = 1 + math.log(count, 2)
                    
                tfidf_factor = 0.0
                if term in dict_corpus:
                    dict_corpus_term_length = len(dict_corpus[term].keys())
                    if dict_corpus_term_length > 0:   
                        idf_factor = math.log((float(corpus_length)/float(dict_corpus_term_length)), 2)
                    else:
                        idf_factor = 0.0
                        
                tfidf_factor = tf_factor * idf_factor
                query_vector.append(tfidf_factor)
           
        normalization_factor = 0.0
        for tfidf in query_vector:
            normalization_factor += tfidf * tfidf
        
        normalization_factor = math.sqrt(normalization_factor)
        
        if normalization_factor != 0.0:
            query_vector = [x/normalization_factor for x in query_vector]
        else:
            query_vector = [0.0 for x in query_vector]
        
        return query_vector
    
    
    """
    calculateTFIDFofDocs
    parameters: 
        1. tokens/terms of query
        2. dictionary with key as the term and value as the dictionary with key as the tweetID and
             value as the normalized tf-idf
    returns: 
    """
    '''
    def calculateTFIDFofDocs(self, query_terms, final_corpus_dict):
        dictwithDocTFIDFVector = {}
        
        for term in query_terms:
            if term not in final_corpus_dict:
                continue
            else:
                temp_dict = final_corpus_dict[term]
                
                for key, value in temp_dict.items():
                    docVector = []
                    if key in dictwithDocTFIDFVector:
                        docVector = list(dictwithDocTFIDFVector[key])
                    
                    docVector.append(value)    
                    dictwithDocTFIDFVector[key] = docVector
                
        return dictwithDocTFIDFVector
    '''
    
    def calc_TFIDFofDocs(self, query_terms, final_corpus_dict, query_vector):
        final_dict = {}
        query_vector_index = 0
        
        for term in query_terms:
            if term not in final_corpus_dict:
                #query_vector_index += 1
                continue
            else:
                temp_dict = final_corpus_dict[term]
                
                for key, value in temp_dict.items():
                    if key in final_dict:
                        final_dict[key] += query_vector[query_vector_index] * value
                    else:
                        final_dict[key] = query_vector[query_vector_index] * value
                    
                query_vector_index += 1
                
        return final_dict
        
    '''
    def calculateDotProduct(self, vector1, vector2):
        resultingVector = [a*b for a,b in zip(vector1,vector2)]
        finalSum = sum(resultingVector)
        return finalSum
    '''
    
    def dict_ID_text(self, tweets):
        dict = {}
        
        for tweet in tweets:
            try:
                #tweet = simplejson.loads(unicode(tweet),encoding="UTF-8")
                tweet = simplejson.loads(tweet)
                dict[tweet['id']] = tweet['text'].encode('ascii', 'ignore').lower()
                #dict[tweet['id']] = tweet['text'].lower()
            except ValueError:
                pass
            
        return dict
    
    def main(self, flag):
        if len(sys.argv) != 2:
            print "usage: ./CosineSimilarity.py <file to read json data(tweets)>"
            sys.exit(1)
        
        filename = sys.argv[1]
        f = file(filename, "r")
        tweets = f.readlines()
        corpus_length = len(tweets)
        
        start = time()
        
        dict_corpus = self.create_dict(tweets)
        dictWithIDAndText = self.dict_ID_text(tweets)
        updated_dict = self.updateDictWithIDF(dict_corpus, corpus_length)
        normalized_dict = self.calculateNormalizationFactorForEachDoc(updated_dict)
        final_corpus_dict = self.updateDictWithDocNormFactor(updated_dict, normalized_dict)
        
        if flag == False:
            return final_corpus_dict, dict_corpus, corpus_length, dictWithIDAndText
        
        print "Processing time:", time()-start
                
        while True:
            input_query = raw_input("Enter query: ")
            
            query_terms = self.split_text(input_query)
            query_vector = self.calculateTFIDFVectorofQueryTerm(query_terms, dict_corpus, corpus_length)
            #print query_vector
            #dictwithDocTFIDFVectors = cosineSimilarity.calculateTFIDFofDocs(query_terms, final_corpus_dict)
            
            final_dict = self.calc_TFIDFofDocs(query_terms, final_corpus_dict, query_vector)
            
            '''
            final_dict = {}
        
            for key, value in dictwithDocTFIDFVectors.items():
                final_dict[key] = cosineSimilarity.calculateDotProduct(query_vector, value)
            '''   
            final_list = sorted(final_dict.items(), key=lambda x: x[1], reverse=True)
            
            
            new_list = [x[0] for x in final_list]
            new_list_length = len(new_list)
            
            if new_list_length == 0:
                print "Sorry, no match :("
            elif new_list_length >= 50:
                for index in range(50):
                    val = new_list[index]
                    #print final_list[index], dictWithIDAndText[val]
                    print index+1, new_list[index], dictWithIDAndText[val]
            else:
                for index in range(new_list_length):
                    val = new_list[index]
                    #print final_list[index], dictWithIDAndText[val]
                    print index+1, new_list[index], dictWithIDAndText[val]
                          
        return
            
    
if __name__ == '__main__':
    
    cosineSimilarity = CosineSimilarity()
    final_list = cosineSimilarity.main(True)
                
        
    
   




        
