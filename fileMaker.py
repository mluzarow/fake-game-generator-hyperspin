# Python 2.7.8

from os import listdir, makedirs
from os.path import isfile, join
from bs4 import BeautifulSoup
from string import maketrans

class OutputFile:
	def __init__ (self, name, crc):
		self.name = name
		self.crc = crc
	
	def sanitize (self):
		trans = maketrans ('\/:?"<>|', '        ')
		self.name.translate (trans)

def dumpFakeFiles (nameList, root):
	makedirs (root)
	
	for fileName in nameList:
		with open ('%s/%s.txt' % (root, fileName.name), 'w') as f:
			f.write ('\0\0\0\0')
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
	
	games = list ()
	
	for tag in gameTags:
		name = tag['name']
		crc = tag.crc.string
		
		currentGame = OutputFile (name, crc)
		currentGame.sanitize ()
		
		games.append (currentGame)
	
	dumpFakeFiles (games, XMLfileName[0:-4])

