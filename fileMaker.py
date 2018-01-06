# Python 2.7.8

import os, sys, zlib
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

def modify_file_crc32(path, newcrc, printstatus=False):
	with open(path, "r+b") as raf:
		raf.seek(0, os.SEEK_END)
		
		# Read entire file and calculate original CRC-32 value
		crc = get_crc32(raf)
		if printstatus:
			print("Original CRC-32: {:08X}".format(reverse32(crc)))
		
		# Compute the change to make
		delta = crc ^ newcrc
		delta = multiply_mod(0xCBF1ACDA, delta)
		
		# Patch 4 bytes in the file
		raf.seek(0)
		bytes4 = bytearray(raf.read(4))
		if len(bytes4) != 4:
			raise IOError("Cannot read 4 bytes at offset")
		for i in range(4):
			bytes4[i] ^= (reverse32(delta) >> (i * 8)) & 0xFF
		raf.seek(0)
		raf.write(bytes4)
		if printstatus:
			print("Computed and wrote patch")
		
		# Recheck entire file
		if get_crc32(raf) != newcrc:
			raise AssertionError("Failed to update CRC-32 to desired value")
		elif printstatus:
			print("New CRC-32: {:08X}".format(reverse32(get_crc32(raf))))
			print("New CRC-32 successfully verified")

def get_crc32(raf):
	raf.seek(0)
	crc = 0
	while True:
		buffer = raf.read(128 * 1024)
		if len(buffer) == 0:
			return reverse32(crc & MASK)
		else:
			crc = zlib.crc32(buffer, crc)

def reverse32(x):
	y = 0
	for i in range(32):
		y = (y << 1) | (x & 1)
		x >>= 1
	return y
	
def multiply_mod(x, y):
	# Russian peasant multiplication algorithm
	z = 0
	while y != 0:
		z ^= x * (y & 1)
		y >>= 1
		x <<= 1
		if (x >> 32) & 1 != 0:
			x ^= POLYNOMIAL
	return z

# def pow_mod(x, y):
# 	# Exponentiation by squaring
# 	z = 1
# 	while y != 0:
# 		if y & 1 != 0:
# 			z = multiply_mod(z, x)
# 		x = multiply_mod(x, x)
# 		y >>= 1
# 	return z

# def divide_and_remainder(x, y):
# 	if y == 0:
# 		raise ValueError("Division by zero")
# 	if x == 0:
# 		return (0, 0)
# 
# 	ydeg = get_degree(y)
# 	z = 0
# 	for i in range(get_degree(x) - ydeg, -1, -1):
# 		if (x >> (i + ydeg)) & 1 != 0:
# 			x ^= y << i
# 			z |= 1 << i
# 	return (z, x)

# def reciprocal_mod(x):
# 	# Based on a simplification of the extended Euclidean algorithm
# 	y = x
# 	x = POLYNOMIAL
# 	a = 0
# 	b = 1
# 	while y != 0:
# 		q, r = divide_and_remainder(x, y)
# 		c = a ^ multiply_mod(q, b)
# 		x = y
# 		y = r
# 		a = b
# 		b = c
# 	if x == 1:
# 		return a
# 	else:
# 		raise ValueError("Reciprocal does not exist")

# def get_degree(x):
# 	return x.bit_length() - 1

def fakeCRC (gameFile, root):
	targetCRC = int (gameFile.crc, 16)
	
	if targetCRC & MASK != targetCRC:
		return "Error: Invalid new CRC-32 value"
	
	targetCRC = reverse32(targetCRC)

	modify_file_crc32("%s/%s.txt" % (root, gameFile.name), targetCRC, True)

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

POLYNOMIAL = 0x104C11DB7
MASK = (1 << 32) - 1

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

