import dbus
import dbus.service
import dbus.glib
import abc

import config
import tools


class Service(object) :
	__metaclass__ = abc.ABCMeta

	def __init__(self) :
		self.__shared_objects_list = []

	@abc.abstractmethod
	def initService(self) :
		pass

	@abc.abstractmethod
	def closeService(self) :
		pass

	def addSharedObject(self, shared_object) :
		self.__shared_objects_list = []

	def sharedObjects(self) :
		return self.__shared_objects_list


class CustomObject(dbus.service.Object) :
	def __init__(self, object_path) :
		dbus.service.Object.__init__(self, config.value("runtime", "bus_name"), object_path)

		self.__object_path = object_path

	def objectPath(self) :
		self.__object_path

class NativeObject(CustomObject) :
	def __init__(self, object_path) :
		CustomObject.__init__(self, tools.joinPath(config.value("service", "path"), object_path))


def customMethod(interface_name) :
	def decorator(function) :
		return dbus.service.method(interface_name)(function)
	return decorator

def nativeMethod(interface_name) :
	def decorator(function) :
		return customMethod(tools.joinMethod(config.value("service", "name"), interface_name))(function)
	return decorator

