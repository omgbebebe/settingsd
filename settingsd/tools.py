def __joinItems(separator, first, *others_list) :
	for others_list_item in others_list :
		if len(first) == 0 :
			first = others_list_item
		else :
			first += separator + others_list_item
	return first

def joinPath(first, *others_list) :
	return __joinItems("/", first, *others_list)

def joinMethod(first, *others_list) :
	return __joinItems(".", first, *others_list)

