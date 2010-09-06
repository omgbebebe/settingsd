import sys
sys.path.append("..") # path hook
import settingsd.service


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

class Requisites(settingsd.service.Requisites) :
	@classmethod
	def serviceName(self) :
		return "hello"

	@classmethod
	def options(self) :
		return [
			("hello", "hello_string", "Hello, World!", str)
		]

class Service(settingsd.service.Service) :
	def init(self) :
		self.Functions.addSharedObject("Hello", Hello("hello"))

	def close(self) :
		pass

