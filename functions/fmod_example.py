# -*- coding: utf-8 -*-


import time

from settingsd import config
from settingsd import service
from settingsd import shared


##### Private constants #####
SERVICE_NAME = "example"

EXAMPLE_METHODS_NAMESPACE = "example"
SETTINGSD_SHARED_OBJECT_METHODS_NAMESPACE = "com.example.settingsd.sharedObject"
DBUS_METHODS_NAMESPACE = "dbus"


##### Private classes #####
class Example(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(EXAMPLE_METHODS_NAMESPACE, out_signature="s")
	def hello(self) :
		return config.value(self.service().serviceName(), "hello_string")

	@service.functionMethod(EXAMPLE_METHODS_NAMESPACE, in_signature="s", out_signature="s")
	def echo(self, text) :
		return text

	@service.functionMethod(EXAMPLE_METHODS_NAMESPACE, out_signature="s")
	def time(self) :
		return time.ctime()

	###

	@service.customMethod(SETTINGSD_SHARED_OBJECT_METHODS_NAMESPACE)
	def die(self) :
		self.removeFromConnection() # shared.Functions.test.example.removeFromConnection()
		self.shared().removeSharedObject(self.name()) # shared.Functions.test.removeSharedObject("example")

	@service.customMethod(SETTINGSD_SHARED_OBJECT_METHODS_NAMESPACE, out_signature="s")
	def path(self) :
		return service.FunctionObject.path(self)

	###

	@service.functionMethod(DBUS_METHODS_NAMESPACE, in_signature="s")
	def dbusEcho(self, text) :
		self.dbusEchoSignal(text)

	@service.functionSignal(DBUS_METHODS_NAMESPACE, signature="s")
	def dbusEchoSignal(self, text) :
		pass


##### Public classes #####
class Service(service.Service) :
	def initService(self) :
		shared.Functions.addShared("test")
		shared.Functions.test.addSharedObject(SERVICE_NAME, Example(SERVICE_NAME, self))

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "hello_string", "Hello, World!", str)
		]

