
#================== Imports ===================#
# NOTE: External Functions Should Return Something...
from blacklist import *
import socket
from sys import *
from string import *
from smtplib import *
from datetime import *
from subprocess import *



#================ Initializaion ===============# 
#================ Global Files ================# 
Config = open("config.txt", 'r+')
NDFile = open("NickDictionary.txt", 'r+') #Username is different than Nick
MailTo = open("MailTo.txt", 'r+')
Log = open("log.txt", 'w')

def GetConfig():
	global Config
	exit = False

	line = Config.readline().strip('\n')
	linelist = line.split(" = ")
	return str(linelist[1]).strip(' \r\n')


def ConvertToList(string):
	list = string.split(", ")
	return list
	
def Stamp():
	i = datetime.now()
	retval = str(i.strftime('%m/%d/%Y %H:%M:%S\t'))
	return retval

def log(string):
	info = Stamp() + string + "\r\n"
	Log.write(info)

def LoadNickDictionary(dictionary):
	for line in NDFile:
		entry = line.strip("\n")
		entries = entry.split(" = ")
		nickname = entries[0]
		username = entries[1]
		dictionary[nickname] = username
	return dictionary
	
def LoadMailList(list):
	for line in MailTo:
		list.append(line)
	return list
	
def Email(sender, message):
	print "Sending email..."
	fromvar = "From: " + sender
	Popen(["./email.sh", fromvar, message])

	
def RollCall(message, sender):
	query = message.split(' ')
	if len(query) == 3:
		return ("May I Invite You To Kiss My Shiny Metal Ass?")
		

#============ Function Definitions ============#	



BufferSize = int(GetConfig()) 

Host = GetConfig()
Port = int(GetConfig())

ServerName = GetConfig() #In case different than Host

Nick = GetConfig()
Identity = GetConfig()
RealName = GetConfig()
Channels = ConvertToList(GetConfig())

Prefix = GetConfig()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((Host, Port))

log("Connecting to the IRC Server...")



log("Connected to IRC Server. Signing In...")
s.send("NICK %s\r\n" % Nick)
s.send("USER %s %s bla :%s\r\n" % (Identity, Host, RealName))

log("Signed In. Joining Channels...")
for x in Channels:
	print "Joining " + x + "..."
	s.send("JOIN " + x + "\r\n")

def say(target, message):
	s.send("PRIVMSG " + target + " :" + message + "\r\n")	



#============== Global Variables ==============#
NickDict = {}

MailList = []

AFKList = []

NickDict = LoadNickDictionary(NickDict)
	
MailList = LoadMailList(MailList)


log("The Bot is Up and Running")


NDFile.close()

from commands import *

def ProcessAdminCommand(command, message):
	global NickDict
	
	if command == "blacklist":
		AddToBlacklist(input[1])
		
		retval = input[1] + " added to Blacklist."
	elif command == "whitelist":
		RemoveFromBlacklist(input[1])
		retval = input[1] + " removed from Blacklist."
	elif command == "status":
		if Blacklisted(input[1]):
			retval = "Status: Blacklisted"
		else:
			retval = "Status: Whitelisted"
	elif command == "clear":
		if input[1] == "blacklist":
			ClearBlacklist()
	elif command == "reset":
		if input[1] == "blacklist":
			ClearBlacklist()
		elif input[1] == "nickdict":
			NickDict = {}
	elif command == "addnick":
		NickDict[input[1]] = input[2]

	else:
		retval = "Arf???"

	return retval
	
def ProcessUserCommand(command, parameters, sender, nick):
	if CommandList.count(command)!=0:
		func = CommandDict.get(command)
		retval = func(parameters, nick)
	else:
		retval = None
	return retval	

#=========== Main Method Definition ===========#
def main():
	Start = datetime.now()
	index = 0

	global PWhiteList, DoorServer, DoorPort
	while True:
		stop = datetime.now()
		elapsed = stop - Start
		if elapsed > timedelta(minutes=3):
			print "Clearing SenderList"
			ClearSenderList()
			if elapsed > timedelta(minutes=90):
				log("Clearing Blacklist...")
				ClearBlacklist()
			Start = datetime.now()
	
		data = s.recv(BufferSize)
		log(data)
		print data
		if data.find("PING :" + ServerName)!=-1:
			s.send('PONG ' + data.split()[1]+'\r\n') 
		
		elif data.find("PRIVMSG") != -1:
			
			data1 = data.split(':')
			header = data1[1].split('!')
			nick = header[0]
			header1 = header[1].split('@')
			sender = header1[0]
			header2 = header1[1].split("PRIVMSG ")
			target = str(header2[1]).strip(' ')

			while AFKList.count(sender) > 0:
				AFKList.remove(sender)
			
			if data1.__len__() >= 4:
				whoto = data1[2].lower()
				message = data1[3].strip(' \r\n\t')
				
			else:
				whoto = None
				message = data1[2].strip(' \r\n\t')
					
			lmessage = message.lower()

			if target == Nick:
				target = nick
				if message.find(Prefix) == -1:
					whoto = Nick.lower()
				pm = True
			else:
				pm = False
			
			if not Blacklisted(sender):
				if MailList.count(whoto) > 0:

					if not Online(whoto):
						UpdateBlacklist(sender, whoto)
						say(target, "He is not online at the moment. I'll pass along the message.")
						Email(sender, whoto, message)
						log("Message Sent to " + whoto)
				elif whoto == Nick.lower():
					input = lmessage.split(' ')
					command = input[0]
					if PWhitelist.count(sender) > 0:
						answer = ProcessAdminCommand(command, input)
					elif CommandList.count(command) > 0:
						input.remove(command)
						answer = ProcessUserCommand(command, input, sender, nick)
					else:
						answer = "Arf???"
					if answer != None:
							say(target, answer)

				elif whoto == None and lmessage.find("bot roll call") !=-1:
					if not pm:
						UpdateBlacklist(sender, "RollCall")

					answer = RollCall(lmessage, sender)
					if answer != None:
						say(target, answer)
				
				elif whoto == None and lmessage.find(Prefix) !=-1:
					if lmessage[:1] == Prefix:
						parameters = lmessage.split(' ')
						command = parameters[0].strip('#')
						parameters.remove(parameters[0])
						if not pm:
							UpdateBlacklist(sender, command)
						answer = ProcessUserCommand(command, parameters, sender, nick)
						if answer != None:
							for x in answer:
								say(target, x)

#============ Main Method Referral ============#
if __name__ == "__main__":
    main()	
