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


##### Public classes #####
class Server(object) :
	def __init__(self) :
		object.__init__(self)

		#####

		self._modules_list = []
		self._services_dict = {}

		self._main_loop = gobject.MainLoop()


	### Public ###

	def runLoop(self) :
		logger.verbose("Running GObject loop...")
		self._main_loop.run()

	def quitLoop(self) :
		self._main_loop.quit()
		logger.verbose("GObject loop closed")

	###

	def loadModules(self) :
		sys.path.append(const.FUNCTIONS_DIR)
		sys.path.append(const.ACTIONS_DIR)

		for modules_path_list_item in (const.FUNCTIONS_DIR, const.ACTIONS_DIR) :
			for module_name in [ item[:-3] for item in os.listdir(modules_path_list_item) if item.endswith(".py") ] :
				try :
					self._modules_list.append(__import__(module_name, globals(), locals(), [""]))
				except :
					logger.error("Import error on module \"%s\"" % (module_name))
					logger.attachException()
					continue

				self._services_dict[self._modules_list[-1].Service.serviceName()] = {
					"service_class" : self._modules_list[-1].Service,
					"service" : None
				}

				logger.verbose("Loaded module: %s" % (module_name))

		sys.path.remove(const.FUNCTIONS_DIR)
		sys.path.remove(const.ACTIONS_DIR)

	###

	def loadServerConfigs(self) :
		config.loadConfigs(only_sections_list = (config.APPLICATION_SECTION,))

	def loadServicesConfigs(self) :
		for service_name in self._services_dict.keys() :
			service_options_list = list(self._services_dict[service_name]["service_class"].optionsList())
			service_options_list.append((service_name, "enabled", "no", validators.validBool))

			for service_options_list_item in service_options_list :
				try :
					config.setValue(*service_options_list_item)
				except :
					logger.error("Error on set options tuple %s" % (str(service_options_list_item)))
					logger.attachException()

		config.loadConfigs(exclude_sections_list = (config.APPLICATION_SECTION,))

	###

	def initBus(self) :
		bus_type = config.value(config.APPLICATION_SECTION, "bus_type")
		service_name = config.value(config.APPLICATION_SECTION, "service_name")

		try :
			config.setValue(config.RUNTIME_SECTION, "bus_name", dbus.service.BusName(service_name,
				( dbus.SystemBus() if bus_type == const.BUS_TYPE_SYSTEM else dbus.SessionBus() )))
		except :
			logger.error("Could not connect to D-Bus \"%s\"" % (bus_type))
			logger.attachException()
			raise

		logger.verbose("Connected to D-Bus \"%s\" as \"%s\"" % (bus_type, service_name))

	###

	def initServices(self) :
		for service_name in self._services_dict.keys() :
			if config.value(service_name, "enabled") :
				try :
					self._services_dict[service_name]["service"] = self._services_dict[service_name]["service_class"]()
					self._services_dict[service_name]["service"].initService()
				except :
					logger.error("Cannot initialize service \"%s\"" % (service_name))
					logger.attachException()

	def closeServices(self) :
		for service_name in self._services_dict.keys() :
			if self._services_dict[service_name]["service"] != None :
				try :
					self._services_dict[service_name]["service"].closeService()
					del self._services_dict[service_name]["service"]
				except :
					logger.error("Cannot close service \"%s\"" % (service_name))
					logger.attachException()
				self._services_dict[service_name]["service"] = None

