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

	octets_list = arg.split(".")
	if len(octets_list) != 4 :
		raise ValidatorError("Argument \"%s\" is not valid IPv4 address" % (arg))

	for count in xrange(4) :
		try :
			octets_list[count] = int(octets_list[count])
			if not 0 <= octets_list[count] <= 255 :
				raise Exception
		except :
			raise ValidatorError("Argument \"%s\" is not valid IPv4 address" % (arg))

	return (arg, octets_list)

def validIpv4Netmask(arg) :
	arg = str(arg).strip()

	octets_list = arg.split(".")
	if len(octets_list) == 1 :
		try :
			arg = int(arg)
			if not 0 <= arg <= 32 :
				raise ValidatorError("Argument \"%s\" is not valid IPv4 netmask" % (arg))
		except :
			raise ValidatorError("Argument \"%s\" is not valid IPv4 netmask" % (arg))

		octets_list = [0] * 4
		one_count = arg
		for count in xrange(4) :
			octet_one_count = 8
			while one_count and octet_one_count :
				octets_list[count] |= 128 >> 8 - octet_one_count
				one_count -= 1
				octet_one_count -= 1
	elif len(octets_list) == 4 :
		for count in xrange(4) :
			try :
				octets_list[count] = int(octets_list[count])
				if not 0 <= octets_list[count] <= 255 :
					raise Exception
			except :
				raise ValidatorError("Argument \"%s\" is not valid IPv4 netmask" % (arg))
	else :
		raise ValidatorError("Argument \"%s\" is not valid IPv4 netmask" % (arg))

	return (arg, octets_list)

def validMacAddress(arg) :
	arg = str(arg).strip()

	octets_list = arg.split(":")
	if len(octets_list) != 6 :
		raise ValidatorError("Argument \"%s\" is not valid MAC address" % (arg))

	for count in xrange(6) :
		try :
			octets_list[count] = int(octets_list[count], 16)
			if not 0 <= octets_list[count] <= 255 :
				raise Exception
		except :
			raise ValidatorError("Argument \"%s\" is not valid MAC address" % (arg))

	return (arg, octets_list)

