#!/usr/local/bin/python2.6

# written by Lukas Pirl <placebo@lukas-pirl.de> 2011
# neither code quality nor performance was considered
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys, string, os, pwd, time
from random import choice
from collections import namedtuple

# ###########################
# configuration
#
verbose=False
users_gid=5100
users_min_count=500
#
# ###########################

DbConnnectInfo = namedtuple("DatabaseAccountInfo", ['server', 'database', 'user', 'password'])

def log(msg, error=False):
	if error:
		sys.stdout.write("\n")
		sys.stderr.write("ERROR: "+msg+"\n")
	else:
		if verbose or not msg.strip().startswith("#"):
			sys.stdout.write(msg)
			sys.stdout.write("\n")

def generate_password(length=12):
	chars=string.letters + string.digits
	return ''.join([choice(chars) for i in range(length)])

def ask_if_simulate():
	log("### asking NOT to simulate actions ###")
	if os.isatty(sys.stdout.fileno()) and os.isatty(sys.stdin.fileno()):
		simulate_pass = generate_password(5)
		prompt = "Do you want me *NOT* to simulate actions?\n"
		prompt += "Please be make a dry run and be *very* sure that everything is alright.\n"
		prompt += "For NOT simulation mode (may be DESTRUCTIVE), please type '%s': " % simulate_pass
		return simulate_pass != raw_input(prompt)
	else:
		return True

def get_user_list():
	users=set()
	for user in pwd.getpwall():
		if user[3] == users_gid:
			users.add(user[0])
	if len(users) < users_min_count:
		log("userlist seems to short...check configuration", True)
		exit(1)
	return users

def user_name_db(user):
	return user.lower().replace(".", "_")

def get_user_list_db(users):
	return set([user_name_db(user) for user in users])

def get_set_from_file(filename, add_iterable):
	today = int(time.strftime("%Y%m%d",time.localtime(time.time())))
	return_set = set()
	for line in open(filename, "r"):
		line = line.strip()
		if not line.startswith("#"):
			line = line.split(",")
			if int(line[1]) >= today or int(line[1])==0:
				return_set.add(line[0])
	return (return_set | set(add_iterable))
