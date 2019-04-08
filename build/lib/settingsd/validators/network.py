# -*- coding: utf-8 -*-


from .common import ValidatorError


##### Public methods #####
def validIpv4Address(arg) :
	arg = str(arg).strip()

	octets_list = arg.split(".")
	if len(octets_list) != 4 :
		raise ValidatorError("Argument \"%s\" is not valid IPv4 address" % (arg))

	for count in range(4) :
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
		for count in range(4) :
			octet_one_count = 8
			while one_count and octet_one_count :
				octets_list[count] |= 128 >> 8 - octet_one_count
				one_count -= 1
				octet_one_count -= 1
	elif len(octets_list) == 4 :
		for count in range(4) :
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

	for count in range(6) :
		try :
			octets_list[count] = int(octets_list[count], 16)
			if not 0 <= octets_list[count] <= 255 :
				raise Exception
		except :
			raise ValidatorError("Argument \"%s\" is not valid MAC address" % (arg))

	return (arg, octets_list)

