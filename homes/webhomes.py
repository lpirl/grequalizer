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

from common import *
import os, sys

# ###########################
# configuration
#
simulate=False
users_newdir_mode=int('711', 8)
userdir_root="/mnt/data/webhome"
#~ known_directories_filename="known_webhomes.txt"
#~ trash_root=userdir_root + "/deprecated"
#
# ###########################

def get_dirs(path):
	dirs = set()
	for path_found in os.listdir(path):
		if os.path.isdir(path+path_found):
			dirs.add(path_found)
	return dirs

def modify_userdir(user, target, source=None):
	if os.path.exists(target):
		log("cannot use directory '%s'. Already exists!" % target, True)
		return
	if not source==None:
		if os.path.exists(source):
			if not simulate:
				os.rename(source, target)
			else:
				log("would move '%s' -> '%s'" % (source, target))
			return
	if not simulate:
		os.mkdir(target)
		if not user == None:
			user = pwd.getpwnam(user)
			os.chown(target, user[2], user[3])
			os.chmod(target, users_newdir_mode)
	else:
		log("would create '%s' and set rights" % target)



log("### getting user list ###")
users = get_user_list()



log("### checking environment ###")
if os.path.isdir(os.path.dirname(sys.argv[0])):
	os.chdir(os.path.dirname(sys.argv[0]))
if not userdir_root.endswith(os.sep):
	userdir_root += os.sep
#~ if not trash_root.endswith(os.sep):
	#~ trash_root += os.sep
if not os.path.isdir(userdir_root):
	log("could not find user directory root!", True)
	exit(1)
#~ if not os.path.isdir(trash_root):
	#~ log("could not find trash, creating...")
	#~ os.makedirs(trash_root)
#~ if not os.path.isfile(known_directories_filename):
	#~ log("could not find '%s' with known directories" % known_directories_filename, True)
	#~ exit(1)


log("### getting user directories ###")
userdirs = get_dirs(userdir_root)
users_lower = set([user.lower() for user in users])


log("### checking if all user directories are lowercase ###")
for userdir in userdirs:
	if not userdir.islower() and userdir.lower() in users_lower:
		log("directory %s is not lower case, moving..." % userdir)
		modify_userdir(userdir, userdir_root+userdir.lower(), userdir_root+userdir)
userdirs = get_dirs(userdir_root)


log("### checking if every user has a directory ###")
for user in users.difference(userdirs):
	if user.lower() not in userdirs:
		log("%s has no directory, creating..." % user)
		modify_userdir(user, userdir_root+user.lower())



#~ log("### getting additionally known directories ###")
#~ today = int(time.strftime("%Y%m%d",time.localtime(time.time())))
#~ known_dirs = set()
#~ for line in open(known_directories_filename, "r"):
	#~ line = line.strip()
	#~ if not line.startswith("#"):
		#~ line = line.split(",")
		#~ if int(line[1]) >= today or int(line[1])==0:
			#~ known_dirs.add(line[0])


#~
#~ log("### checking for unknown directories ###")
#~ for directory in userdirs.difference(users.union(known_dirs)):
	#~ log("%s is a unkown directory" % directory)
	#~ modify_userdir(None, trash_root+directory, userdir_root+directory)
