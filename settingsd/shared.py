# -*- coding: utf-8 -*-


#####
class SharedConflict(Exception) :
	pass

class SharedNotExist(Exception) :
	pass


#####
class SharedMeta(type) :
	def __init__(cls, name, bases_list, attrs_dict) :
		cls._shared_objects_dict = {}

	def addSharedObject(cls, shared_object_name, shared_object) :
		if cls._shared_objects_dict.has_key(shared_object_name) :
			raise SharedConflict("Shared \"%s\" is already exists in collection \"%s\"" % (shared_object_name, cls.__name__))

		cls._shared_objects_dict[shared_object_name] = shared_object
		setattr(cls, shared_object_name, shared_object)

	def removeSharedObject(cls, shared_object_name) :
		if not cls._shared_objects_dict.has_key(shared_object_name) :
			raise SharedNotExist("Shared \"%s\" does not exist in collection \"%s\"" % (shared_object_name, cls.__name__))

		cls._shared_objects_dict.pop(shared_object_name)
		delattr(cls, shared_object_name)

	def hasSharedObject(cls, shared_object) :
		return ( shared_object in cls._shared_objects_dict.keys() or shared_object in cls._shared_objects_dict.values() )

	def sharedObject(cls, shared_object_name) :
		return cls._shared_objects_dict[shared_object_name]

	def sharedObjectsList(cls) :
		return cls._shared_objects_dict

class Functions(object) :
	__metaclass__ = SharedMeta

class Actions(object) :
	__metaclass__ = SharedMeta

