# Python 2.7.8

from os import listdir, makedirs
from os.path import isfile, join
from bs4 import BeautifulSoup
from string import maketrans

class OutputFile:
    def __init__ (self, name, crc):
        self.name = name

        if (crc == None):
            self.crc = ''
        else:
            self.crc = crc

    def sanitize (self):
        trans = maketrans ('\/:?"<>|', '        ')
        self.name.translate (trans)

    def generateFileName (self):
        return ('%s %s' % (self.crc, self.name)).strip ()

def dumpFakeFiles (nameList, root):
    makedirs (root)
    
    for fileName in nameList:
        with open ('%s/%s.txt' % (root, fileName.generateFileName ()), 'w') as f:
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

flagCRC = None

while (flagCRC == None):
    crcInclude = raw_input ('Include CRC values [y/n]? ').lower ()
    
    if (crcInclude == 'y' or crcInlude == 'yes'):
        flagCRC = True
    elif (crcInclude == 'n' or crcInclude == 'no'):
        flagCRC = False

files = getFileList (path)

for XMLfileName in files:
    gameTags = readXML ('%s/%s' % (path, XMLfileName))
    
    games = list ()
    
    for tag in gameTags:
        name = tag['name']

        if (flagCRC):
            crc = tag.crc.string
        else:
            crc = ''
        
        currentGame = OutputFile (name, crc)
        currentGame.sanitize ()
        
        games.append (currentGame)
        
    dumpFakeFiles (games, XMLfileName[0:-4])
    
        
