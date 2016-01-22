#Commands Class for IRC 
#from main import DoorServer
import socket
from main import NickDict
from main import AFKList
from blacklist import *
from subprocess import *

AFKList = []
VoteStatus = False
VoteOptions = []
Results = []
VoteNumber = 0
Voted = []

def GetFile():
	filename = "vote" + str(VoteNumber)
	f = open(filename, 'w+')
	return f

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
			
def IsOnline(parameters, sender, pm):
	retval = []
	if len(parameters) > 0:
		for x in parameters:
			if x == "k9":
				retval.append(sender + ": I'm right here. No need to shout!\n")
			elif Online(x.lower()):
				if AFKList.count(x) > 0:
					retval.append(x + " has an SSH Tunnel Open, but is AFK\n")
				else:
					retval.append(x + " has an SSH Tunnel Open, and is probably on the server somewhere.\n")
			else:
				retval.append(x + " does not appear to be connected to Yakko at the moment.\n")
	else:
		retval.append(sender + ": Incorrect Syntax. Type #online <user1> <user2>... to see if he/she is online.\n")

	return retval



def Door(parameters, sender, pm):
	retval = []
	DoorServer = "shrek.dhcp.io"
	DoorPort = 1357
	DoorBot = socket.socket()
	DoorBot.connect((DoorServer, DoorPort))
	DoorBot.send("door status\r\n")
	doorState = DoorBot.recv(1024)
	DoorBot.close()
	if doorState.find("open") != -1:
		parameters = []
		response = Office(parameters, sender, None)
		temp = response[0].split(" - ")
		list1 = temp[0]
		retval.append(list1 + "; " + doorState)
	else:
		retval.append(doorState)
		
	return retval

def Help(parameter, sender, pm):
	retval = []
	if len(parameter) == 0 or len(parameter) > 1:
		retval.append("Available Commands: " + ', '.join(CommandList))
	elif CommandList.count(parameter[0]) == 0:
		retval.append(sender + ": No such command.")
		retval.append("Available Commands: " + ', '.join(CommandList))
	else:
		switcher = {
			"afk": ": Set's a Users AFK (Away From Keyboard) Status",
			"help": ": Type #help <command> for help.",
			"online": ": Checks to see if <users> have SSH tunnels open (doesn't work on nicks).\nType #online <user1> <user2>... to see if he/she is online.",
			"status": ": Type #status <user1> <user2>... to see if he/she is blacklisted.",
			"door": ": Type #door to see if the office door is open.\nType #door open to open door and #door close to close it.",
			"doorbell": ": Type #doorbell -s to see doorbell status. Type #doorbell to ring the doorbell.",
			"dbell": ": Alias for the doorbell command. Type #help doorbell for more information.",
			"bell": " Alias for the doorbell command. Type #help doorbell for more information.",
			"office": ": Type #office to see who's there or #office Flags MACAddress. Flags(function) = -r(Register), -d(DeRegister), and -l(list).",
			"vote": ": Type #vote to see if there is a vote open. Type #vote <vote> to respond to vote. Flags(-s (Start a vote), -e (End a vote)."
		}
		response = sender + switcher.get(parameter[0], "")
		retval.append(response)
	return retval
		
def Status(parameters, sender, pm):
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

def Office(parameters, sender, pm):
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
	
def SetAFK(parameter, sender, pm):
	retval = []
	AFKList.append(sender)
        retval.append("Setting " + sender + " as AFK")

def UpdateAFKList(name):
	while AFKList.count(name) != 0:
		AFKList.remove(name)

def Vote(parameters, sender, pm):
	global VoteStatus
	global Results
	global VoteOptions
	global VoteNumber
	retval = []
	#Only allow certain people to end vote.
	#
	if parameters.__len__() == 0:
		if VoteStatus:
			retval.append("A vote is active. Your options are: " + ", ".join(VoteOptions))
		else:
			retval.append("There is no vote taking place at the moment.")
	elif parameters.__len__() == 1 and VoteStatus:
		if parameters[0] == "-e":
			VoteStatus = False
			ResultDict = {}
			if Results.__len__() > 0:
				Winner = max(set(Results), key=Results.count)
			else:
				Winner = "Null"			

			for x in VoteOptions:
				VoteOptions.remove(x)
			
			for x in Voted:
				Voted.remove(x)

			for x in Results:
				y = ResultDict.get(x)
				print x
				print y
				if y == None:
					ResultDict[x] = 1
				else:
					ResultDict[x] = ResultDict[x] + 1
			for x in Results:
				Results.remove(x)
					
			f = GetFile()
		
			retval.append("The Winner Is: " + str(Winner))

			for x in ResultDict:
				f.write(str(x) + ": " + str(ResultDict[x]) + " votes.\n")
			f.close()
			VoteNumber += 1			

		elif Voted.count(sender) > 0:
			retval.append("You have already voted.")
		else:
			selection = parameters[0].lower()
			if VoteOptions.count(selection) > 0:
				Results.append(selection)
				Voted.append(sender)
				retval.append("Thank You. Your vote has been counted.")
			else:
				retval.append("That is not a valid option.")
			
			
	else:
		if parameters[0] == "-s":
			VoteStatus = True
			parameters.remove(parameters[0])
			VoteOptions = map(str.lower,parameters)
			print join(VoteOptions)
			retval.append("The Vote has started.")
		elif parameters.__len__() == 1:
			retval.append("There is no vote occuring now.")
		else:
			retval.append("Not a valid use of the command. Type #help vote for more info.")
					
	return retval

def DoorBell(parameters, sender, pm):
	retval = []
	if not pm:
		DoorServer = "shrek.dhcp.io"
		DoorPort = 1357
		DoorBot = socket.socket()
		DoorBot.connect((DoorServer, DoorPort))
		message = sender + ": ring bell\r\n"
		DoorBot.send(message)
		BellState = DoorBot.recv(1024)		
		DoorBot.close()
		retval.append(BellState)

	else:
		retval.append("This Function is not Available in PM")
	return retval



CommandList = ["help", "online", "status", "door", "doorbell", "dbell", "bell", "office", "afk", "vote"]

CommandDict = {
	"help":Help,
	"online":IsOnline,
	"status":Status,
	"door":Door,
	"doorbell":DoorBell,
	"dbell":DoorBell,
	"bell":DoorBell,
	"office":Office,
	"afk":SetAFK,
	"vote":Vote,
	}



