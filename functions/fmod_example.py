# -*- coding: utf-8 -*-


import time

from settingsd import config
from settingsd import service
from settingsd import shared


##### Private constants #####
SERVICE_NAME = "example"


##### Private classes #####
class Example(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod("example")
	def hello(self) :
		return config.value(self.service().serviceName(), "hello_string")

	@service.functionMethod("example")
	def echo(self, text) :
		return text

	@service.functionMethod("example")
	def time(self) :
		return time.ctime()

	###

	@service.customMethod("com.example.settingsd.sharedObject")
	def die(self) :
		self.removeFromConnection() # shared.Functions.test.example.removeFromConnection()
		self.shared().removeSharedObject(self.name()) # shared.Functions.test.removeSharedObject("example")

	@service.customMethod("com.example.settingsd.sharedObject")
	def path(self) :
		return service.FunctionObject.path(self)

	###

	@service.functionMethod("dbus")
	def dbusEcho(self, text) :
		self.dbusEchoSignal(text)

	@service.functionSignal("dbus")
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

