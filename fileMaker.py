# Python 2.7.8

from os import listdir, makedirs
from os.path import isfile, join
from bs4 import BeautifulSoup
from string import maketrans

def dumpFakeFiles (nameList, root):
    makedirs (root)
    
    for fileName in nameList:
        with open ('%s/%s.txt' % (root, fileName), 'w') as f:
                f.write ('')
        f.closed

def readXML (path):
    with open (path, 'r') as f:
        data = f.read()
    f.closed
    
    return (BeautifulSoup(data, "lxml").find_all ('game'))

def getFileList (path):
    return [item for item in listdir(path) if isfile(join(path, item))]

path = raw_input ("Path to XMLs: ")
files = getFileList (path)

for XMLfileName in files:
    gameTags = readXML ('%s/%s' % (path, XMLfileName))

    gameNames = list()
    
    for tag in gameTags:
        name = tag['name']
        trans = maketrans('\/:?"<>|', '        ')
        gameNames.append(name.translate(trans))
        
    dumpFakeFiles (gameNames, XMLfileName[0:-4])
    
        
