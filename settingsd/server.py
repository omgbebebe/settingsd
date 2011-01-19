# -*- coding: utf-8 -*-


import sys
import os
import dbus
import dbus.service
import dbus.glib
import gobject

import const
import config
import logger
import validators.common


##### Public classes #####
class Server(object) :
	def __init__(self) :
		object.__init__(self)

		#####

		self.__modules_list = []
		self.__services_dict = {}

		gobject.threads_init()
		self.__main_loop = gobject.MainLoop()


	### Public ###

	def runLoop(self) :
		logger.verbose("Running GObject loop...")
		self.__main_loop.run()

	def quitLoop(self) :
		self.__main_loop.quit()
		logger.verbose("GObject loop closed")

	###

	def loadModules(self) :
		for modules_path_list_item in (const.FUNCTIONS_DIR, const.ACTIONS_DIR, const.CUSTOMS_DIR) :
			logger.debug("Processing directory \"%s\"..." % (modules_path_list_item))
			sys.path.append(modules_path_list_item)

			for module_name in [ item[:-3] for item in os.listdir(modules_path_list_item)
				if item.endswith(".py") and not item.startswith(".") ] :

				try :
					self.__modules_list.append(__import__(module_name, globals(), locals(), [""]))
				except :
					logger.error("Import error on module \"%s\"" % (module_name))
					logger.attachException()
					continue

				self.__services_dict[self.__modules_list[-1].Service.serviceName()] = {
					"service_class" : self.__modules_list[-1].Service,
					"service" : None
				}

				logger.verbose("Loaded module: %s" % (module_name))

			sys.path.remove(modules_path_list_item)

	###

	def loadServerConfigs(self) :
		config.loadConfigs(only_sections_list = (config.APPLICATION_SECTION,))

	def loadServicesConfigs(self) :
		for service_name in self.__services_dict.keys() :
			service_options_list = list(self.__services_dict[service_name]["service_class"].options())
			service_options_list.append((service_name, "enabled", "no", validators.common.validBool))

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
		for service_name in self.__services_dict.keys() :
			if config.value(service_name, "enabled") :
				logger.verbose("Enabling service \"%s\"..." % (service_name))
				try :
					self.__services_dict[service_name]["service"] = self.__services_dict[service_name]["service_class"]()
					self.__services_dict[service_name]["service"].initService()
				except :
					logger.error("Cannot initialize service \"%s\"" % (service_name))
					logger.attachException()
				logger.info("Initialized service: %s" % (service_name))

	def closeServices(self) :
		for service_name in self.__services_dict.keys() :
			if self.__services_dict[service_name]["service"] != None :
				logger.verbose("Disabling service \"%s\"..." % (service_name))
				try :
					self.__services_dict[service_name]["service"].closeService()
					del self.__services_dict[service_name]["service"]
				except :
					logger.error("Cannot close service \"%s\"" % (service_name))
					logger.attachException()
				self.__services_dict[service_name]["service"] = None
				logger.info("Closed service: %s" % (service_name))

