import sys
sys.path.append("..") # path hook
import settingsd.service


class Hello(settingsd.service.NativeObject) :
	@settingsd.service.nativeMethod("test")
	def hello(self) :
		return "Hello, World!"

	@settingsd.service.nativeMethod("test")
	def echo(self, text) :
		return text

	@settingsd.service.customMethod("org.liksys.settingsd")
	def dump(self) :
		return str(self)

class Service(settingsd.service.Service) :
	def initService(self) :
		self.addSharedObject(Hello("hello"))

	def closeService(self) :
		pass

