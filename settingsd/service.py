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


#####
class Service(object) :
	__metaclass__ = abc.ABCMeta

	Functions = shared.Functions
	Actions = shared.Actions

	@abc.abstractmethod
	def initService(self) :
		pass

	def closeService(self) :
		pass

	@classmethod
	@abc.abstractmethod
	def serviceName(self) :
		pass

	@classmethod
	def options(self) :
		return []


#####
class CustomObject(dbus.service.Object) :
	def __init__(self, object_path) :
		dbus.service.Object.__init__(self, config.value(const.RUNTIME_NAME, "bus_name"), object_path)

		self._object_path = object_path

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


######
def tracer(function) :
	def wrapper(self, *args_list, **kwargs_dict) :
		return_value = function(self, *args_list, **kwargs_dict)
		if config.value(const.MY_NAME, "log_level") == const.LOG_LEVEL_DEBUG :
			logger.message(logger.DEBUG_MESSAGE, "Called \"%s::%s\" with args (%s, %s) --> %s" % (
				self.__class__.__name__, function.__name__, str(args_list), str(kwargs_dict),  str(return_value) ))
		return return_value

	wrapper.__dict__ = function.__dict__
	wrapper.__name__ = function.__name__

	return wrapper

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

