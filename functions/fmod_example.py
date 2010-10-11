# -*- coding: utf-8 -*-


import time

from settingsd import config
from settingsd import service
from settingsd import shared


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
		self.removeFromConnection() # shared.Functions.Test.Example.removeFromConnection()
		self.shared().removeSharedObject(self.name()) # shared.Functions.Test.removeSharedObject("Example")

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
		shared.Functions.addShared("Test")
		shared.Functions.Test.addSharedObject("Example", Example(self.serviceName(), self))

	@classmethod
	def serviceName(self) :
		return "example"

	@classmethod
	def options(self) :
		return [
			(self.serviceName(), "hello_string", "Hello, World!", str)
		]

