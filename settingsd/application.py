# -*- coding: utf-8 -*-


import sys
import os
import dbus
import dbus.service
import dbus.glib
import gobject

import const
import config
import validators
import logger


#####
class Application(object) :
	def __init__(self) :
		object.__init__(self)

		self._bus_name = None

		self._modules_list = []
		self._services_dict = {}

		self._main_loop = gobject.MainLoop()

	def exec_(self) :
		self.init()
		logger.message(const.LOG_LEVEL_INFO, "Initialized")
		try :
			self.run()
		except KeyboardInterrupt :
			self.close()
		logger.message(const.LOG_LEVEL_INFO, "Closed")

	def init(self) :
		self.loadModules()
		self.loadConfigs()
		self.initBus()
		self.initServices()

	def run(self) :
		self._main_loop.run()

	def close(self) :
		self.closeServices()
		self._main_loop.quit()


	def loadModules(self) :
		sys.path.append(const.FUNCTIONS_DIR)
		sys.path.append(const.ACTIONS_DIR)

		for modules_path_list_item in (const.FUNCTIONS_DIR, const.ACTIONS_DIR) :
			for module_name in [ item[:-3] for item in os.listdir(modules_path_list_item) if item.endswith(".py") ] :
				self._modules_list.append(__import__(module_name, globals(), locals(), [""]))
				if self._modules_list[-1].Requisites.serviceName() != None :
					self._services_dict[self._modules_list[-1].Requisites.serviceName()] = {
						"requisites" : self._modules_list[-1].Requisites,
						"service" : self._modules_list[-1].Service,
						"instance" : None
					}
				else :
					print >> sys.stderr, "Anonymous modules does not acceped"

		sys.path.remove(const.FUNCTIONS_DIR)
		sys.path.remove(const.ACTIONS_DIR)

	def loadConfigs(self) :
		for service_name in self._services_dict.keys() :
			service_options_list = list(self._services_dict[service_name]["requisites"].options())
			service_options_list.append((service_name, "enabled", "no", validators.validBool))

			for service_options_list_item in service_options_list :
				config.setValue(*service_options_list_item)

		config.loadConfig()

	def initBus(self) :
		if config.value("service", "bus_type") == const.SERVICE_BUS_TYPE_SYSTEM :
			bus = dbus.SystemBus()
		else :
			bus = dbus.SessionBus()
		self._bus_name = dbus.service.BusName(config.value("service", "name"), bus = bus)
		config.setValue("runtime", "bus_name", self._bus_name)

	def initServices(self) :
		for service_name in self._services_dict.keys() :
			if config.value(service_name, "enabled") :
				self._services_dict[service_name]["instance"] = self._services_dict[service_name]["service"]()
				self._services_dict[service_name]["instance"].init()

	def closeServices(self) :
		for service_name in self._services_dict.keys() :
			if self._services_dict[service_name]["instance"] != None :
				self._services_dict[service_name]["instance"].close()
				del self._services_dict[service_name]["instance"]
				self._services_dict[service_name]["instance"] = None

