
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

OK_CHARS = list("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&* .,-_?:\r\n")

def IsSafe(string):
	string = string.lower()
	for x in string:
		if OK_CHARS.count(x) == 0:
			return False
	return True


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
	Log  = open("log.txt", "a")
	info = Stamp() + string + "\r\n"
	Log.write(info)
	Log.close()

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
	log("Sending Email...")
	print "Sending Email..."
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

def join(channel):
	channel = "#" + channel
	print "Joining " + channel + "..."
	s.send("JOIN " + channel + "\r\n")


for x in Channels:
	log("Joining " + x + "...")
	print "Joining " + x + "..."
	join(x)

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

def ProcessAdminCommand(command, message, nick):
	global NickDict
	
	if command == "blacklist":
		AddToBlacklist(message[0])
		
		ret = message[0] + " added to Blacklist."
		retval = [ret,]	
	elif command == "whitelist":
		RemoveFromBlacklist(message[0])
		ret = message[0] + " removed from Blacklist."
		retval = [ret,]
	elif command == "status":
		if Blacklisted(message[0]):
			retval = ["Status: Blacklisted",]
		else:
			retval = ["Status: Whitelisted",]
	elif command == "clear":
		if message[0] == "blacklist":
			ClearBlacklist()
			retval = ["Blacklist Cleared",]
	elif command == "reset" or command == "refresh":
		if message[0] == "blacklist":
			ClearBlacklist()
			retval = ["Blacklist Cleared",]
		elif message[0] == "nickdict":
			NickDict = {}
			retval = ["Nick Dictionary Cleared",]
		elif message[0] == "commands":
			from commands import *
			retval = ["Commands List Refreshed",]
	elif command == "addnick":
		NickDict[message[0]] = message[1]
		retval = ["Nick Added",]

	elif command == "join":
		print "\"" + message[0] + "\""
		#join(message[0])
		s.send("JOIN #" + message[0] + "\r\n") 
		retval = ["Done.",]
	elif CommandList.count(command) != 0:
		func = CommandDict.get(command)
		retval = func(message, nick, True)
	else:
		retval = ["Arf???",]

	return retval
	
def ProcessUserCommand(command, parameters, sender, nick, pm):
	if CommandList.count(command)!=0:
		func = CommandDict.get(command)
		retval = func(parameters, nick, pm)
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
			log("Clearing Senderlist")
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
		
		elif data.find("PRIVMSG") != -1 and IsSafe(data):
			data1 = data.split(':')
			header = data1[1].split('!')
			nick = header[0]
			header1 = header[1].split('@')
			sender = header1[0]
			header2 = header1[1].split("PRIVMSG ")
			target = str(header2[1]).strip(' ')

			UpdateAFKList(nick)
			
			if data1.__len__() >= 4:
				whoto = data1[2].lower()
				message = data1[3].strip(' \r\n\t')
					
			else:
				whoto = None
				message = data1[2].strip(' \r\n\t')
							
			lmessage = message.lower().strip(' \r\n\t')

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
					input1 = message.split(' ')
					command = input1[0]
					if PWhitelist.count(sender) > 0:
						input1.remove(command)
						answer = ProcessAdminCommand(command, input1, nick)
					elif CommandList.count(command) > 0:
						input1.remove(command)
						answer = ProcessUserCommand(command, input1, sender, nick, pm)
					else:
						answer = []
						answer.append("Arf???")
					if answer != None:
						for x in answer:
							say(target, x)

				elif whoto == None and lmessage.find("bot roll call") !=-1:
					if not pm:
						update = UpdateBlacklist(sender, "RollCall")
						if update != None:
							say(target, update)

						answer = RollCall(lmessage, sender)
						if answer != None:
							say(target, answer)
					
				elif whoto == None and lmessage.find(Prefix) !=-1:
						print message
						if lmessage[:1] == Prefix:
							parameters = message.split(' ')
							command = parameters[0].strip('#')
							parameters.remove(parameters[0])
							if not pm:
								update = UpdateBlacklist(sender, command)
								if update != None:
									say(target, update)
								answer = ProcessUserCommand(command, parameters, sender, nick, pm)
								if answer != None:
									for x in answer:
										say(target, x)
							else:
								answer = ProcessUserCommand(command, parameters, sender, nick, pm)
								if answer != None:
									for x in answer:
										say(target, x)

			
#============ Main Method Referral ============#
if __name__ == "__main__":
    main()	
