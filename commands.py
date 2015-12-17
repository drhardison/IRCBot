#Commands Class for IRC 
#from main import DoorServer
import socket
from main import NickDict
from main import AFKList
from blacklist import *
from subprocess import *

AFKList = []

def Online(user):
	global NickDict
	if user in NickDict:
		user = NickDict.get(user)
	output,error = Popen(["pgrep", "ssh", "-U", user], stdout = PIPE, stderr = PIPE).communicate()
	pid = output.split('\n')
	if pid[0].isdigit():
		return True
	else:
		return False
			
def IsOnline(parameters, sender):
	print parameters
	retval = []
	if len(parameters) > 0:
		for x in parameters:
			if x == "k9":
				retval.append(sender + ": I'm right here. No need to shout!\n")
			elif Online(x):
				retval.append(x + " has an SSH Tunnel Open, and is probably on the server somewhere.\n")
			else:
				retval.append(x + " does not appear to be connected to Yakko at the moment.\n")
	else:
		retval.append(sender + ": Incorrect Syntax. Type #online <user1> <user2>... to see if he/she is online.\n")

	return retval



def Door(parameters, sender):
	retval = []
	DoorServer = "shrek.dhcp.io"
	DoorPort = 1357
	DoorBot = socket.socket()
	DoorBot.connect((DoorServer, DoorPort))
	DoorBot.send("status\r\n")
	doorState = DoorBot.recv(1024)
	DoorBot.close()
	if doorState.find("open") != -1:
		parameters = []
		response = Office(parameters, sender)
		print response
		temp = response[0].split(" - ")
		list1 = temp[0]
		retval.append(list1 + "; " + doorState)
	else:
		retval.append(doorState)
		
	return retval

def Help(parameter, sender):
	retval = []
	if len(parameter) == 0 or len(parameter) > 1:
		retval.append("Available Commands: " + ', '.join(CommandList))
	elif CommandList.count(parameter[0]) == 0:
		retval.append(sender + ": No such command.")
		retval.append("Available Commands: " + ', '.join(CommandList))
	else:
		switcher = {
			"help": ": Type #help <command> for help.",
			"online": ": Checks to see if <users> have SSH tunnels open (doesn't work on nicks).\nType #online <user1> <user2>... to see if he/she is online.",
			"status": ": Type #status <user1> <user2>... to see if he/she is blacklisted.",
			"door": ": Type #door to see if the office door is open.\nType #door open to open door and #door close to close it.",
			"office": ": Type #office to see who's there or #office Flags MACAddress. Flags(function) = -r(Register), -d(DeRegister), and -l(list).",
		}
		response = switcher.get(parameter[0], "")
		retval.append(response)
	return retval
		
def Status(parameters, sender):
	retval = []
	if len(parameters) > 0:
		for x in parameters:
			if Blacklisted(x):
				retval.append(x + " is blacklisted.")
			else:
				retval.append(x + " isn't blacklisted.")
	else:
		retval.append(sender + ": Incorrect Syntax. Type #status user.")
	
	return retval

def Office(parameters, sender):
	url = "shrek.dhcp.io:5001/"
	retval = []
	command = ""
	if len(parameters) == 0:
		command = "plain"
		output,error = Popen(["curl", "-s", "-m", "10", url+command ], stdout = PIPE, stderr=PIPE).communicate()
		retval.append(output)
	elif len(parameters) == 1:
		flag = parameters[0]
		if flag == "-l":
			command = "list/"
			output,error = Popen(["curl", "-s", "-m", "10", url+command+sender], stdout = PIPE, stderr=PIPE).communicate()
			retval.append(output)
	elif len(parameters) == 2:
		flag = parameters[0]
		param = parameters[1]
		if flag == "-r":
			command = "reg"
			postvar = "nick=" + sender + "&mac=" + param
			output,error = Popen(["curl", "-s", "-m", "10", "-d", postvar, url+command], stdout = PIPE, stderr=PIPE).communicate()
			retval.append(output)
		elif flag == "-d":
			command = "dereg"
			postvar = "nick=" + sender + "&mac=" + param
			output,error = Popen(["curl", "-s", "-m", "10", "-d", postvar, url+command], stdout = PIPE, stderr=PIPE).communicate()
			retval.append(output)
		else:
			retval.append("Invalid Syntax. Flag Options are -r,-d and -l.")
	else:
		retval.append("Invalid Syntax. Format is #office -flag parameters")		
		
	return retval
	
def SetAFK(parameter, sender):
	AFKList.append(sender)

CommandList = ["help", "online", "status", "door", "office", "afk"]

CommandDict = {
	"help":Help,
	"online":IsOnline,
	"status":Status,
	"door":Door,
	"office":Office,
	"afk":SetAFK,
	}



