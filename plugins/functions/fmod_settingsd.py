# -*- coding: utf-8 -*-


from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared

import settingsd.tools as tools
import settingsd.tools.dbus


##### Private constants #####
SETTINGSD_METHODS_NAMESPACE = tools.dbus.joinMethod(const.DEFAULT_SERVICE_NAME, "commonInfo.settingsd")
LOGGER_METHODS_NAMESPACE = tools.dbus.joinMethod(const.DEFAULT_SERVICE_NAME, "logger")
APPLICATION_METHODS_NAMESPACE = tools.dbus.joinMethod(const.DEFAULT_SERVICE_NAME, "application")


##### Private classes #####
class Settingsd(service.CustomObject) :

	### DBus methods ###

	@service.customMethod(SETTINGSD_METHODS_NAMESPACE, out_signature="s")
	def version(self) :
		return const.VERSION

	@service.customMethod(SETTINGSD_METHODS_NAMESPACE, out_signature="s")
	def versionStatus(self) :
		return const.VERSION_STATUS

	@service.customMethod(SETTINGSD_METHODS_NAMESPACE, out_signature="i")
	def functionalityLevel(self) :
		return const.FUNCTIONALITY_LEVEL

	###

	@service.customMethod(LOGGER_METHODS_NAMESPACE, in_signature="i")
	def setLogLevel(self, log_level) :
		config.setValue(config.APPLICATION_SECTION, "log_level", log_level)

	###

	@service.customMethod(APPLICATION_METHODS_NAMESPACE)
	def quit(self) :
		config.value(config.RUNTIME_SECTION, "application").quit()


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(const.MY_NAME, Settingsd(const.DEFAULT_SERVICE_PATH, self))

	@classmethod
	def serviceName(self) :
		return const.MY_NAME

