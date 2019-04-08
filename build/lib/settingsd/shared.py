# -*- coding: utf-8 -*-


##### Exceptions #####
class SharedsConflict(Exception) :
	pass

class SharedNotExists(Exception) :
	pass

class SharedObjectsConflict(Exception) :
	pass

class SharedObjectNotExists(Exception) :
	pass


##### Private classes #####
class SharedAbstract :
	def __init__(entity) :
		entity._shareds_dict = {}
		entity._shared_objects_dict = {}

		#####

		entity._parent_shared = None


	### Public ###

	def setParentShared(entity, shared) :
		entity._parent_shared = shared

	def parentShared(entity) :
		return entity._parent_shared

	###

	def name(entity) :
		if entity.parentShared() == None :
			return None
		for (shared_name, shared) in list(entity.parentShared().shareds().items()) :
			if shared == entity :
				return shared_name
		return None

	###

	def addShared(entity, shared_name) :
		if shared_name in entity._shareds_dict :
			raise SharedsConflict("Shared \"%s\" is already exists in collection \"%s\"" % (shared_name, entity.__name__))

		entity._shareds_dict[shared_name] = Shared()
		entity._shareds_dict[shared_name].setParentShared(entity)
		setattr(entity, shared_name, entity._shareds_dict[shared_name])

	def removeShared(entity, shared_name) :
		if shared_name not in entity._shareds_dict :
			raise SharedNotExists("Shared \"%s\" does not exist in collection \"%s\"" % (shared_name, entity.__name__))

		entity._shareds_dict[shared_name].setParentShared(None)
		entity._shareds_dict.pop(shared_name)
		delattr(entity, shared_name)

	def hasShared(entity, shared_name) :
		return shared_name in entity._shareds_dict

	def shared(entity, shared_name) :
		return entity._shareds_dict[shared_name]

	def shareds(entity) :
		return entity._shareds_dict

	###

	def addSharedObject(entity, shared_object_name, shared_object) :
		if shared_object_name in entity._shared_objects_dict :
			raise SharedObjectsConflict("Shared object \"%s\" is already exists in collection \"%s\"" % (shared_object_name, entity.__name__))

		entity._shared_objects_dict[shared_object_name] = shared_object
		entity._shared_objects_dict[shared_object_name].setShared(entity)
		setattr(entity, shared_object_name, entity._shared_objects_dict[shared_object_name])

	def removeSharedObject(entity, shared_object_name) :
		if shared_object_name not in entity._shared_objects_dict :
			raise SharedObjectNotExists("Shared object \"%s\" does not exist in collection \"%s\"" % (shared_object_name, entity.__name__))

		entity._shared_objects_dict[shared_object_name].setShared(None)
		entity._shared_objects_dict.pop(shared_object_name)
		delattr(entity, shared_object_name)

	def hasSharedObject(entity, shared_object) :
		return ( shared_object in entity._shared_objects_dict or shared_object in list(entity._shared_objects_dict.values()) )

	def sharedObject(entity, shared_object_name) :
		return entity._shared_objects_dict[shared_object_name]

	def sharedObjects(entity) :
		return entity._shared_objects_dict

class SharedRootMeta(type, SharedAbstract) :
	def __init__(cls, name, bases_list, attrs_dict) :
		type.__init__(cls, name, bases_list, attrs_dict)
		SharedAbstract.__init__(cls)

class Shared(SharedAbstract) :
	def __init__(self) :
		object.__init__(self)
		SharedAbstract.__init__(self)


##### Public classes #####
class Functions(object, metaclass=SharedRootMeta) :
	@classmethod
	def name(self) :
		return "Functions"

class Actions(object, metaclass=SharedRootMeta) :
	@classmethod
	def name(self) :
		return "Actions"

class Customs(object, metaclass=SharedRootMeta) :
	@classmethod
	def name(self) :
		return "Customs"

