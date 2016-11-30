from nltk.corpus import wordnet as wn
import nltk
import re
import sys
import simplejson
from collections import Counter
from CosineSimilarity import *
from PageRank import *


"""
split_text
parameters: string
returns: list of tokens    
"""
def split_string(text):
    text = re.compile("[^\w]|_").sub(" ", text)
    word_list = re.findall("\w+", text)    
    return word_list

def split_text(text):
    list = []
    text_dash = re.sub('(http://\S+|\S*[^\w\s]\S*)',' ',text)
    list.extend(re.findall(r'[A-Z].\w+', text_dash))
    return list


"""
It finds out the 100 most popular words in the user description of all the tweets.
Actually, we want to s
"""
def findMostPopularWords(tweets):    
    list = []
    for tweet in tweets:
        tweet = simplejson.loads(unicode(tweet),encoding="UTF-8")
        
        if 'description' in tweet['user']:
            text = tweet['user']['description']
            text_dash = re.sub('(http://\S+|\S*[^\w\s]\S*)',' ',text)
            list.extend(re.findall(r'[A-Z].\w+', text_dash))
        
    list = [x.lower() for x in list]
    final_list = Counter(list).most_common(100)
    
    return final_list
    
def taggedUsers_dict(tweets, dict_buckets):
    dict = {}
    
    for tweet in tweets:
        tweet = simplejson.loads(unicode(tweet),encoding="UTF-8")
        userID = tweet['user']['id']
        
        if 'description' in tweet['user']:
            text = tweet['user']['description']
            splitted_text = split_string(text.lower())
            
            if userID not in dict:
                dict[userID] = []
                
            for term in splitted_text:
                if term in dict_buckets: 
                    dict[userID].append(dict_buckets[term])

            
    for key, value in dict.items():
        dict[key] = list(set(value))
        
    return dict
        
def staticDictOfBuckets():
    list_social = ['social', 'love', 'lover', 'college', 'internet', 'web', 'twitter', 'media', 'news']
    list_technology = ['science', 'tech', 'university', 'software', 'geek', 'computer']
    list_professional = ['professional', 'director', 'editor', 'marketing', 'writer', 'manager', 'freelance', 'ceo', 'producer', 'developer']
    list_sports = ['sports', 'game', 'star', 'fan']
    
    dict_buckets = {}
    
    for elem in list_social:
        dict_buckets[elem] = 'social'
        
    for elem in list_technology:
        dict_buckets[elem] = 'technology'
        
    for elem in list_professional:
        dict_buckets[elem] = 'professional'
        
    for elem in list_sports:
        dict_buckets[elem] = 'sports'
        
    return dict_buckets

def update_dictionary(global_dict, tagged_dict):
    '''
    new_dict = {}
    
    usersInCategory = []
    for key, value in tagged_dict.items():
        if category in value:
            usersInCategory.append(key)
    
    for key, value in global_dict.items():
        if key in usersInCategory:
            new_dict[key] = []
        
        if len(value) > 0:
            for val in value:
                if val in usersInCategory:
                    if val in global_dict:
                        new_dict[key].append(val)
    '''
                        
                        
    universal_dict = {}
    
    for key, values in global_dict.items():
        if key in tagged_dict:
            if len(values) > 0:
                common_tags = []
                for value in values:
                    if value in tagged_dict:
                        common_tags = list(set(tagged_dict[key]).intersection(tagged_dict[value])) 
                        
                        for tag in common_tags:
                            temp_list = []
                            temp_dict = {}
                            if tag in universal_dict:
                                if key in universal_dict[tag]:
                                    universal_dict[tag][key].append(value)
                                else:
                                    temp_list.append(value)
                                    universal_dict[tag][key] = temp_list
                            else:
                                temp_list.append(value)
                                temp_dict[key] = temp_list
                                universal_dict[tag] = temp_dict
        else:
            continue
                        
    return universal_dict
    
    

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print "usage: ./TopicSensitivePageRank.py <file to read json data(tweets)>"
        sys.exit(1)
            
    filename = sys.argv[1]
    f = file(filename, "r")
    tweets = f.readlines()
    
    #final_list = findMostPopularWords(tweets)
      
    dict_buckets = staticDictOfBuckets()
    tagged_dict = taggedUsers_dict(tweets, dict_buckets)
    #print tagged_dict
    pageRank = PageRank()
    
    global_dict = pageRank.create_dictionary(tweets)
    idToUserMap = pageRank.map_IDtoUsername(tweets)
    updated_dict = update_dictionary(global_dict, tagged_dict)
    
    for tag in updated_dict:
        print tag, len(updated_dict[tag])

    #print updated_dict_social
    final_dict_social = pageRank.update_dictionary(updated_dict['technology'])
    print final_dict_social
    
    final_list_social = sorted(final_dict_social.items(), key=lambda x: x[1], reverse=True)
    
    final_list_dash = []
    for l in final_list_social:
        final_list_dash.append(l[0])
     
    '''   
    if 'biobio' in final_list_dash:
        print "yes it exists"
    '''
    
    for index in range(50):
        print index+1, final_list_social[index][0], final_list_social[index][1], idToUserMap[final_list_social[index][0]]
    
    
    
    
    
    
    


