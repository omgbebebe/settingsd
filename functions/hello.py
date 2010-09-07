import sys
sys.path.append("..") # path hook
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

class Service(settingsd.service.Service) :
	def initService(self) :
		self.Functions.addSharedObject("Hello", Hello(self.serviceName()))

	@classmethod
	def serviceName(self) :
		return "hello"

	@classmethod
	def options(self) :
		return [
			(self.serviceName(), "hello_string", "Hello, World!", str)
		]

