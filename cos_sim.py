import sys
import re
import math
import os

"""
split_text
parameters: string
returns: list of tokens    
"""
def split_text(text):
    text = re.compile("[^\w]|_").sub(" ", text)
    word_list = re.findall("\w+", text.lower())    
    return word_list
    
            
def create_dict(base_dir):
    file_list = os.listdir(base_dir)
    dict = {}
    
    for file in file_list:
        try:
            filename = os.path.join(base_dir, file)
            f = open(filename, "r")
            text = f.read()
            f.close()
            terms = split_text(text)
            set_terms = set(terms)
            
            for term in set_terms:
                count = 0
                for word in terms:
                    if term == word:
                        count += 1 
                
                temp_dict = {}
                if term in dict:
                    temp_dict = dict[term]
                    temp_dict[file] = 1 + math.log(count, 2)
                else:
                    temp_dict[file] = 1 + math.log(count, 2)
                    
                dict[term] = temp_dict
              
        except ValueError:
            pass
                    
    return dict


def updateDictWithIDF(dict, corpus_length):
    terms = dict.keys()

    for term in terms:
        temp_dict = dict[term]
        docIDList = temp_dict.keys()
        
        if len(docIDList) != 0:
            calculated_idf = math.log(float(corpus_length)/float(len(docIDList)), 2)
        else:
            continue
        
        for docID in docIDList:
            temp_dict[docID] *= calculated_idf
            
        dict[term] = temp_dict
        
    return dict

def calculateNormalizationFactorForEachDoc(dict):
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

def updateDictWithDocNormFactor(dict, normalized_dict):
    terms = dict.keys()
    
    for term in terms:
        temp_dict = dict[term]
        docIDList = temp_dict.keys()
        
        for docID in docIDList:
            temp_dict[docID] = temp_dict[docID]/normalized_dict[docID]
            
        dict[term] = temp_dict
        
    return dict


def calculateTFIDFVectorofQueryTerm(query_terms, dict_corpus, corpus_length):
    set_terms = set(query_terms)
    query_vector = []
    
    for term in set_terms:
        count = 0
        for q_term in query_terms:
            if term == q_term:
                count += 1
                
        tf_factor = 1 + math.log(count, 2)
        
        if len(dict_corpus[term].keys()) > 0 and len(dict_corpus[term].keys() != 1):
            idf_factor = math.log(float(corpus_length)/float(len(dict_corpus[term].keys())), 2)
            tfidf_factor = tf_factor * idf_factor
        
            query_vector.append(tfidf_factor)
        else:
            continue
       
    normalization_factor = 0.00 
    for tfidf in query_vector:
        normalization_factor += tfidf * tfidf
    
    normalization_factor = math.sqrt(normalization_factor)
    
    if normalization_factor != 0:
        query_vector = [x/normalization_factor for x in query_vector]
    
    return query_vector

def calculateTFIDFofDocs(query_terms, final_corpus_dict):
    dictwithDocTFIDFVector = {}
    
    for term in query_terms:
        temp_dict = final_corpus_dict[term]
        
        for key, value in temp_dict.items():
            docVector = []
            if key in dictwithDocTFIDFVector:
                docVector = list(dictwithDocTFIDFVector[key])
            
            docVector.append(value)    
            dictwithDocTFIDFVector[key] = docVector
            
    return dictwithDocTFIDFVector

def calculateDotProduct(vector1, vector2):
    resultingVector = [a*b for a,b in zip(vector1,vector2)]
    finalSum = sum(resultingVector)
    return finalSum
            
           
def main():
    
    if len(sys.argv) != 2:
        print "usage: ./cos_sim.py <base directory to read the files>"
        sys.exit(1)
        
    base_dir = sys.argv[1]
    file_list = os.listdir(base_dir)
    corpus_length = len(file_list)
    
    dict_corpus = create_dict(base_dir)
    updated_dict = updateDictWithIDF(dict_corpus, corpus_length)
    normalized_dict = calculateNormalizationFactorForEachDoc(updated_dict)
    final_corpus_dict = updateDictWithDocNormFactor(updated_dict, normalized_dict)
 
    while True:
        input_query = raw_input("Enter query: ")
        query_terms = split_text(input_query)
        query_vector = calculateTFIDFVectorofQueryTerm(query_terms, dict_corpus, corpus_length)
        dictwithDocTFIDFVectors = calculateTFIDFofDocs(query_terms, final_corpus_dict)
        
        final_dict = {}
        
        for key, value in dictwithDocTFIDFVectors.items():
            final_dict[key] = calculateDotProduct(query_vector, value)
            
        final_list = sorted(final_dict.items(), key=lambda x: x[1], reverse=True)
        
        if len(final_list) == 0:
            print "Sorry the term does not exist in the corpus :("
            
        print final_list

if __name__ == '__main__':
    main() 


        
