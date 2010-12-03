# -*- coding: utf-8 -*-


import re


##### Exceptions #####
class ValidatorError(Exception) :
	pass


##### Public methods #####
def validBool(arg) :
	arg = str(arg).lower()
	true_args_list = ("1", "true", "yes")
	false_args_list = ("0", "false", "no")

	if not arg in true_args_list + false_args_list :
		raise ValidatorError("Argument \"%s\" not in list %s or %s" % (arg, true_args_list, false_args_list))

	return ( arg in true_args_list )

def validRange(arg, valid_args_list) :
	if not arg in valid_args_list :
		raise ValidatorError("Argument \"%s\" not in range %s" % (arg, str(valid_args_list)))
	return arg

def validStringList(arg) :
	return re.split(r"[,\t ]+", str(arg))

###
def validIpv4Address(arg) :
	arg = str(arg).strip()

	octets_list = []
	for octets_list_item in arg.split(".") :
		try :
			octets_list_item = int(octets_list_item)
			if not 0 <= octets_list_item <= 256 :
				raise Exception
			octets_list.append(octets_list_item)
		except :
			raise ValidatorError("Argument \"%s\" is not valid IPv4 address" % (arg))

	if len(octets_list) != 4 :
		raise ValidatorError("Argument \"%s\" is not valid IPv4 address" % (arg))

	return (arg, octets_list)

