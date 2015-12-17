# Blacklist Class for IRC Bot


#================== Imports ===================#
# NOTE: External Functions Should Return Something...
from sys import *
from string import *


#================ Initializaion ===============#
BLFile = None
WLFile = None
PBlacklist = []
PWhitelist = []
Blacklist = []
SenderList = []

def LoadBlacklist(list):
	for line in BLFile:
		line = line.strip("\r\n").lower()
		list.append(line)
	return list

def LoadWhitelist(list):
	for line in WLFile:
		line = line.strip("\r\n").lower()
		list.append(line)
	return list

BLFile = open("blacklist.txt", 'r+') #For Perma-Blacklist
WLFile = open("whitelist.txt", 'r+') #For Perma-Whitelist
	
PBlacklist = LoadBlacklist(PBlacklist)
PWhitelist = LoadWhitelist(PWhitelist)
Blacklist = LoadBlacklist(Blacklist)

BLFile.close()
WLFile.close()
	
#============ Function Definitions ============#

	
def UpdateBlacklist(sender, command):
	print "Updating blacklist with " + sender + "..."
	toadd = (sender, command)

	if (PBlacklist.count(sender) <= 0 and PWhitelist.count(sender) <= 0):
		SenderList.append(toadd)
		print "Added to SenderList"
	if SenderList.count(toadd) > 3:
		print "Adding to blacklist"
		AddToBlacklist(sender)
		return sender + " added to blacklist."
	else:
		return None

def RemoveFromBlacklist(name):
	Blacklist.remove(name)
		
def AddToBlacklist(name):
	Blacklist.append(name)
	
def Blacklisted(sender):
		if Blacklist.count(sender) > 0:
			return True
		elif PBlacklist.count(sender) > 0:
			return True
		else:
			return False
			
def ClearBlacklist():
	Blacklist = []
	
def ClearSenderList():
	SenderList = []
