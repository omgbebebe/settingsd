# -*- coding: utf-8 -*-


import sys

import settingsd.service
import settingsd.shared


class Hello(settingsd.service.FunctionObject) :
	@settingsd.service.functionMethod("test")
	def hello(self) :
		return "Hello, World!"

	@settingsd.service.functionMethod("test")
	def echo(self, text) :
		return text

	@settingsd.service.customMethod("org.liksys.settingsd")
	def dump(self) :
		return str(self)

	@settingsd.service.customMethod("org.liksys.settingsd")
	def die(self) :
		settingsd.shared.Functions.Hello.removeFromConnection()
		settingsd.shared.Functions.removeSharedObject("Hello")

	###

	@settingsd.service.functionMethod("dbus")
	def dbusEcho(self, text) :
		self.dbusEchoSignal(text)

	@settingsd.service.functionSignal("dbus")
	def dbusEchoSignal(self, text) :
		pass


class Service(settingsd.service.Service) :
	def initService(self) :
		self.Functions.addSharedObject("Hello", Hello(self.serviceName()))

	@classmethod
	def serviceName(self) :
		return "hello"

	@classmethod
	def optionsList(self) :
		return [
			(self.serviceName(), "hello_string", "Hello, World!", str)
		]

