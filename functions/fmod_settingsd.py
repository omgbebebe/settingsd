# -*- coding: utf-8 -*-


from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import dbus_tools


##### Private classes #####
class Settingsd(service.CustomObject) :

	### DBus methods ###

	@service.customMethod(dbus_tools.joinMethod(const.DEFAULT_SERVICE_NAME, "logger"))
	def setLogLevel(self, log_level) :
		config.setValue(config.APPLICATION_SECTION, "log_level", log_level)

	###

	@service.customMethod(dbus_tools.joinMethod(const.DEFAULT_SERVICE_NAME, "application"))
	def quit(self) :
		config.value(config.RUNTIME_SECTION, "application").quit()


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject("Settingsd", Settingsd(const.DEFAULT_SERVICE_PATH))

	@classmethod
	def serviceName(self) :
		return const.MY_NAME

