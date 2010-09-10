# -*- coding: utf-8 -*-


import dbus
import dbus.service
import dbus.glib
import abc

import const
import config
import shared
import dbus_tools
import logger


##### Private classes #####
class ServiceInterface(object) :
	__metaclass__ = abc.ABCMeta


	### Public ###

	@abc.abstractmethod
	def initService(self) :
		pass

	def closeService(self) :
		pass

class ServiceRequisitesInterface(object) :
	__metaclass__ = abc.ABCMeta


	### Public ###

	@classmethod
	@abc.abstractmethod
	def serviceName(self) :
		pass

	@classmethod
	def optionsList(self) :
		return []


##### Public classes #####
class Service(ServiceInterface, ServiceRequisitesInterface) :
	Functions = shared.Functions
	Actions = shared.Actions


#####
class CustomObject(dbus.service.Object) :
	def __init__(self, object_path) :
		dbus.service.Object.__init__(self, config.value(const.RUNTIME_NAME, "bus_name"), object_path)

		self._object_path = object_path


	### Public ###

	def objectPath(self) :
		self._object_path

	def addToConnection(self, connection = None, path = None) :
		self.add_to_connection(connection, path)

	def removeFromConnection(self, conneciton = None, path = None) :
		self.remove_from_connection(conneciton, path)


class FunctionObject(CustomObject) :
	def __init__(self, object_path) :
		CustomObject.__init__(self, dbus_tools.joinPath(config.value(const.MY_NAME, "service_path"), "functions", object_path))

class ActionObject(CustomObject) :
	def __init__(self, object_path) :
		CustomObject.__init__(self, dbus_tools.joinPath(config.value(const.MY_NAME, "service_path"), "actions", object_path))


##### Private decorators #####
def tracer(function) :
	def wrapper(self, *args_list, **kwargs_dict) :
		return_value = function(self, *args_list, **kwargs_dict)
		if config.value(const.MY_NAME, "log_level") == const.LOG_LEVEL_DEBUG :
			logger.debug("Called \"%s::%s\" with args (%s, %s) --> %s" % (self.__class__.__name__, function.__name__,
				str(args_list), str(kwargs_dict),  str(return_value) ))
		return return_value

	wrapper.__name__ = function.__name__
	wrapper.__dict__ = function.__dict__
	wrapper.__doc__ = function.__doc__

	return wrapper


##### Public decorators #####
def customMethod(interface_name) :
	def decorator(function) :
		return tracer(dbus.service.method(interface_name)(function))
	return decorator

def functionMethod(interface_name) :
	def decorator(function) :
		return customMethod(dbus_tools.joinMethod(config.value(const.MY_NAME, "service_name"), "functions", interface_name))(function)
	return decorator

def actionsMethod(interface_name) :
	def decorator(function) :
		return customMethod(dbus_tools.joinMethod(config.value(const.MY_NAME, "service_name"), "actions", interface_name))(function)
	return decorator

