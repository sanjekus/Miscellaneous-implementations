import json
from pprint import pprint
import re
import os

def split_text(text):
    text = re.compile("[^\w]|_").sub(" ", text)
    word_list = re.findall("\w+", text.lower())    
    return word_list



path = "C:\\tweets\\"
dir = os.listdir(path)
print dir


json_data=open('tweets.json', 'r')
print json_data
data = json.load(json_data)
pprint(data)
json_data.close()


'''
for fname in dir:
    json = eval(open(path + dir[0]).read())
    json = eval('demo.json'.read())
    # now, json is a normal python object
    print json
    # list all properties...
    print dir(json)


jsonfiles = []
for fname in dir:
    with open(path + fname,'r') as f:
        jsonfiles.append(json.load(f)) 

print jsonfiles[0]
'''

'''
for k,v in data.iteritems():
    print k,v
'''



'''
print data["maps"][0]["id"]
print data["masks"]["id"]
print data["om_points"]
'''