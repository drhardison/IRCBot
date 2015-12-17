# IRCBot
This Repository is for an IRC Bot.
This code may be used as a basis for another IRC bot.

This bot has received many different names, but this iteration was designed to be customizable by editing the config files.

This bot is set to using # as a prefix (as in one types #command <parameters> to talk to bot). This can be changed in the config file.

This bot has some interesting features built in like:
  - Anti-spam (blacklist/whitelist).
  - Email Messaging for "offline" communication
  - Nick resolution (Uses a programmable Nick Dictionary to resolve Nicks to usernames, if different)

This bot has some important files:
  - Config.txt - Contains configuration settings. # of lines should not change, nor should format. Commenting is not supported.
  - log.txt - Log file for the bot.
  - MailTo.txt - a list of users that wish to receive mail notifications when offline.
  - whitelist.txt - a list of users that are permanently whitelisted. (used for admins)
  - blacklist.txt - a list of users that are permanently blacklisted. (used for delinquents)
  - NickDictionary.txt - a list (dictionary) that contains nicks and their associated usernames.

This bot was designed to be modular and as such, most commands can be removed/added in the commands class.
It should be noted that the following things should be updated when adding a new command:
  - The CommandList variable
  - The CommandDict variable
  - One should add an entry into the help dictionary for the new command.

Some commands included are:
  - IsOnline/Online - reports whether or not the user has an SSH tunnel open (or if they have reported themself as AFK)
  - Door - Connects to a python server on a raspberry pi that is connected to a door sensor to see if the door to the office is open.
  - Help - Offers help with syntax and available commands.
  - Office - Uses WMU CClub's DHCP server function to see who is in the CClub office.
  - AFK - (Away From Keyboard) is used to toggle the user's "away" status.
  - Vote - A module by which people can vote for things or answer surveys.
  - More fun/usefull commands to come...

Because the main class takes care of reporting the output of each command to the server, each command function should return a list containing one or more responses.

Questions can be directed to: joseph.m.hagan@wmich.edu

