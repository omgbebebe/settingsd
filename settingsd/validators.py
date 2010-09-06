# -*- coding: utf-8 -*-


#####
class ValidatorError(Exception) :
	pass


##### Public #####
def validBool(arg) :
	arg = str(arg).lower()
	true_args_list = ("1", "true", "yes")
	false_args_list = ("0", "false", "no")

	if not arg in true_args_list + false_args_list :
		raise ValidatorError("Argument \"%s\" not in list %s or %s" % (arg, true_args_list, false_args_list))

	return ( arg in true_args_list )

def validRange(arg, valid_args_list) :
	if not arg in valid_args_list :
		raise ValidatorError("Argument \"%s\" not in list %s" % (arg, valid_args_list))
	return arg

