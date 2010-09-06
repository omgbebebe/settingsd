# -*- coding: utf-8 -*-

import dbus
import dbus.service
import dbus.glib
import abc

import config
import shared
import dbus_tools


#####
class Requisites(object) :
	@classmethod
	def serviceName(self) :
		return None

	@classmethod
	def options(self) :
		return []


#####
class Service(object) :
	__metaclass__ = abc.ABCMeta

	Functions = shared.Functions
	Actions = shared.Actions

	@abc.abstractmethod
	def init(self) :
		pass

	@abc.abstractmethod
	def close(self) :
		pass


#####
class CustomObject(dbus.service.Object) :
	def __init__(self, object_path) :
		dbus.service.Object.__init__(self, config.value("runtime", "bus_name"), object_path)

		self._object_path = object_path

	def objectPath(self) :
		self._object_path

class FunctionObject(CustomObject) :
	def __init__(self, object_path) :
		CustomObject.__init__(self, dbus_tools.joinPath(config.value("service", "path"), "functions", object_path))

class ActionObject(CustomObject) :
	def __init__(self, object_path) :
		CustomObject.__init__(self, dbus_tools.joinPath(config.value("service", "path"), "actions", object_path))


######
def customMethod(interface_name) :
	def decorator(function) :
		return dbus.service.method(interface_name)(function)
	return decorator

def functionMethod(interface_name) :
	def decorator(function) :
		return customMethod(dbus_tools.joinMethod(config.value("service", "name"), "functions", interface_name))(function)
	return decorator

def actionsMethod(interface_name) :
	def decorator(function) :
		return customMethod(dbus_tools.joinMethod(config.value("service", "name"), "actions", interface_name))(function)
	return decorator

