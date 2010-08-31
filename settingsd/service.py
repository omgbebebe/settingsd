import dbus
import dbus.service
import dbus.glib
import abc

import config


class Service(object) :
	__metaclass__ = abc.ABCMeta

	def __init__(self, parent) :
		object.__init__(self)

		self.__parent = parent

		self.__objects_list = []

	@abc.abstractmethod
	def initService(self) :
		pass

	@abc.abstractmethod
	def closeService(self) :
		pass

	def addObject(self, object) :
		self.__objects_list.append(object)

	def objectsList(self) :
		return self.__objects_list

	def parent(self) :
		return self.__parent

	def busName(self) :
		return self.__parent.busName()


class CustomObject(dbus.service.Object) :
	def __init__(self, object_path, parent) :
		dbus.service.Object.__init__(self, parent.busName(), object_path)

		self.__object_path = object_path
		self.__parent = parent

	def parent(self) :
		return self.__parent

	def busName(self) :
		return self.__parent.busName()

	def objectPath(self) :
		return self.__object_path

class NativeObject(CustomObject) :
	def __init__(self, object_path, parent) :
		CustomObject.__init__(self, "%s/%s" % (config.GlobalConfig["service_path"], object_path), parent)


def customMethod(interface_name) :
	def decorator(function) :
		return dbus.service.method(interface_name)(function)
	return decorator

def nativeMethod(interface_name) :
	def decorator(function) :
		return customMethod("%s.%s" % (config.GlobalConfig["service_name"], interface_name))(function)
	return decorator

