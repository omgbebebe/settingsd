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

from service_decorators import customMethod
from service_decorators import functionMethod
from service_decorators import actionMethod

from service_decorators import customSignal
from service_decorators import functionSignal
from service_decorators import actionSignal


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
	pass


#####
class CustomObject(dbus.service.Object) :
	def __init__(self, object_path, shared_path, service) :
		dbus.service.Object.__init__(self, config.value(config.RUNTIME_SECTION, "bus_name"), object_path)

		self._object_path = object_path
		self._shared_path = shared_path
		self._service = service


	### Public ###

	def objectPath(self) :
		return self._object_path

	def sharedPath(self) :
		return self._shared_path

	def service(self) :
		return self._service

	###

	def addToConnection(self, connection = None, path = None) :
		self.add_to_connection(connection, path)

	def removeFromConnection(self, conneciton = None, path = None) :
		self.remove_from_connection(conneciton, path)


class FunctionObject(CustomObject) :
	def __init__(self, object_path, shared_path, service) :
		CustomObject.__init__(self, dbus_tools.joinPath(config.value(config.APPLICATION_SECTION, "service_path"),
			"functions", object_path), shared_path, service)

class ActionObject(CustomObject) :
	def __init__(self, object_path, shared_path, service) :
		CustomObject.__init__(self, dbus_tools.joinPath(config.value(config.APPLICATION_SECTION, "service_path"),
			"actions", object_path), shared_path, service)

