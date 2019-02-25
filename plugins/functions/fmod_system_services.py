# -*- coding: utf-8 -*-


import os
import stat
import re
import pyinotify
from dbus import SystemBus, Interface as DBusInterface

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

from settingsd import validators

import settingsd.tools as tools
import settingsd.tools.dbus
import settingsd.tools.process


##### Private constants #####
SERVICE_NAME = "system_services"

SYSTEM_SERVICES_SHARED_NAME = "system_services"

SYSTEM_SERVICES_OBJECT_NAME = "system_services"

SYSTEM_SERVICE_METHODS_NAMESPACE = "systemService"
SYSTEM_SERVICES_METHODS_NAMESPACE = "systemServices"


##### Private classes #####
class SystemService(service.FunctionObject) :
	def __init__(self, system_service_name, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__system_service_name = system_service_name
		self._bus = SystemBus()
		self._systemd_manager = DBusInterface(self._bus.get_object(
			'org.freedesktop.systemd1', '/org/freedesktop/systemd1'
		), 'org.freedesktop.systemd1.Manager')


	### DBus methods ###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="s")
	def realName(self) :
		return self.__system_service_name

	###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def on(self, levels = None) :
		return self.setLevels(levels, True)

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def off(self, levels = None) :
		return self.setLevels(levels, False)

	###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="")
	def start(self) :
		logger.verbose("{mod}: Request to start service \"%s\"" % (self.__system_service_name))
		self._systemd_manager.StartUnit(self.__system_service_name + '.service', 'replace')

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="")
	def stop(self) :
		logger.verbose("{mod}: Request to stop service \"%s\"" % (self.__system_service_name))
		self._systemd_manager.StopUnit(self.__system_service_name + '.service', 'replace')

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="b")
	def isActive(self) :
		unit = DBusInterface(
			self._bus.get_object(
				'org.freedesktop.systemd1',
				str(self._systemd_manager.LoadUnit(self.__system_service_name + '.service'))
			),
			'org.freedesktop.systemd1.Unit'
		)
		active_state = unit.Get(
			'org.freedesktop.systemd1.Unit',
			'ActiveState',
			dbus_interface='org.freedesktop.DBus.Properties'
		)
		return active_state == 'active' or active_state == 'reloading'


class SystemServices(service.FunctionObject) :
	@service.functionSignal(SYSTEM_SERVICES_METHODS_NAMESPACE)
	def servicesChanged(self) :
		pass


##### Public classes #####
class Service(service.Service, pyinotify.ThreadedNotifier) :
	def __init__(self) :
		service.Service.__init__(self)

		self.__watch_manager = pyinotify.WatchManager()
		pyinotify.ThreadedNotifier.__init__(self, self.__watch_manager, type("EventsHandler", (pyinotify.ProcessEvent,),
			{ "process_IN_CREATE" : self.inotifyEvent, "process_IN_DELETE" : self.inotifyEvent })())

		#####

		self.__system_services = SystemServices(SYSTEM_SERVICES_OBJECT_NAME, self)


	### Public ###

	def initService(self) :
		shared.Functions.addShared(SYSTEM_SERVICES_SHARED_NAME)
		shared.Functions.addSharedObject(SYSTEM_SERVICES_OBJECT_NAME, self.__system_services)

		initd_dir_path = config.value(SERVICE_NAME, "initd_dir")

		logger.verbose("{mod}: First services requset...")
		system_services_shared = shared.Functions.shared(SYSTEM_SERVICES_SHARED_NAME)
		system_service_count = 0
		for system_service_name in os.listdir(initd_dir_path) :
			st_mode = os.stat(os.path.join(initd_dir_path, system_service_name)).st_mode
			if st_mode & stat.S_IEXEC and st_mode & stat.S_IFREG :
				dbus_system_service_name = re.sub(r"[^\w\d_]", "_", system_service_name)

				system_services_shared.addSharedObject(dbus_system_service_name, SystemService(system_service_name,
					tools.dbus.joinPath(SERVICE_NAME, dbus_system_service_name), self))

				system_service_count += 1
		logger.verbose("{mod}: Added %d system services" % (system_service_count))

		###

		self.__watch_manager.add_watch(initd_dir_path, pyinotify.IN_DELETE|pyinotify.IN_CREATE, rec=True)
		self.start()
		logger.verbose("{mod}: Start polling inotify events for \"%s\"" % (initd_dir_path))

	def closeService(self) :
		initd_dir_path = config.value(SERVICE_NAME, "initd_dir")
		self.__watch_manager.rm_watch(self.__watch_manager.get_wd(initd_dir_path))
		self.stop()
		logger.verbose("{mod}: Stop polling inotify events for \"%s\"" % (initd_dir_path))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "initd_dir", "/etc/rc.d/init.d", str),
			(SERVICE_NAME, "chkconfig_bin", "/sbin/chkconfig", str),
			(SERVICE_NAME, "serv_mgr_command", "serv", str)
		]


	### Private ###

	def inotifyEvent(self, event) :
		if event.dir :
			return

		dbus_system_service_name = re.sub(r"[^\w\d_]", "_", event.name)
		system_services_shared = shared.Functions.shared(SERVICE_NAME)

		if event.maskname == "IN_CREATE" :
			system_services_shared.addSharedObject(dbus_system_service_name, SystemService(event.name,
				tools.dbus.joinPath(SERVICE_NAME, dbus_system_service_name), self))

			self.__system_services.servicesChanged()
			logger.verbose("{mod}: Added system service \"%s\"" % (dbus_system_service_name))
		elif event.maskname == "IN_DELETE" :
			system_services_shared.sharedObject(dbus_system_service_name).removeFromConnection()
			system_services_shared.removeSharedObject(dbus_system_service_name)

			self.__system_services.servicesChanged()			
			logger.verbose("{mod}: Removed system service \"%s\"" % (dbus_system_service_name))

