# Python 2.7.8

from os import listdir, makedirs
from os.path import isfile, join
from bs4 import BeautifulSoup
from string import maketrans

class OutputFile:
	def __init__ (self, name, crc):
		self.name = name
		
		if ((crc != None) and (crc != '')):
			self.crc = int (crc, 16)
		else:
			self.crc = None
	
	def sanitize (self):
		trans = maketrans ('\/:?"<>|', '        ')
		self.name.translate (trans)
	
def multiply_mod(x, y):
	z = 0
	while y != 0:
		z ^= x * (y & 1)
		y >>= 1
		x <<= 1
		if (x >> 32) & 1 != 0:
			x ^= 0x104C11DB7
	return z

def reverse32(x):
	y = 0
	for i in range(32):
		y = (y << 1) | (x & 1)
		x >>= 1
	return y

def fakeCRC (gameFile, root):
	targetCRC = reverse32 (gameFile.crc)
	path = "%s/%s.txt" % (root, gameFile.name)
	
	with open(path, "r+b") as f:
		delta = multiply_mod(0xCBF1ACDA, (0x38FB2284 ^ targetCRC))
		
		newData = bytearray(4)
		for i in range(4):
			newData[i] = (reverse32(delta) >> (i * 8)) & 0xff
		
		f.seek(0)
		f.write(newData)

def dumpFakeFiles (nameList, root):
	makedirs (root)
	
	for fileName in nameList:
		with open ('%s/%s.txt' % (root, fileName.name), 'w') as f:
			f.write ('\0\0\0\0')
		f.closed
		
		if (fileName.crc != None):
			fakeCRC (fileName, root)

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

print ("Processing complete.")
