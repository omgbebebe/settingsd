# -*- coding: utf-8 -*-


import re

from common import ValidatorError


##### Public methods #####
def validUserName(arg) :
	if re.match(r"^[a-z_][a-z0-9_-]*$", arg) == None :
		raise ValidatorError("Argument \"%s\" is not valid UNIX user name" % (arg))
	return arg

def validGroupName(arg) :
	if re.match(r"^[a-z_][a-z0-9_-]*$", arg) == None :
		raise ValidatorError("Argument \"%s\" is not valid UNIX group name" % (arg))
	return arg

