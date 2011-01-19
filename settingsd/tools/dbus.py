# -*- coding: utf-8 -*-


##### Public methods #####
def joinPath(first, *others_list) :
	return "/".join((first,) + others_list)

def joinMethod(first, *others_list) :
	return ".".join((first,) + others_list)

