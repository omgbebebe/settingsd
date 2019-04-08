# -*- coding: utf-8 -*-

from dbus import SystemBus, Interface as DBusInterface

from settingsd import service
from settingsd import shared
from settingsd import logger




##### Private constants #####
SERVICE_NAME = "system_services"

SYSTEM_SERVICE_METHODS_NAMESPACE = "systemService"


class SystemServices(service.FunctionObject) :
	def __init__(self, object_path, service_object = None) :
		super().__init__(object_path, service_object)

		self._bus = SystemBus()
		self._systemd_manager = DBusInterface(self._bus.get_object(
			'org.freedesktop.systemd1', '/org/freedesktop/systemd1'
		), 'org.freedesktop.systemd1.Manager')

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s")
	def enable(self, name):
		logger.verbose("{mod}: Request to enable service \"%s\"" % name)
		self._systemd_manager.EnableUnitFiles([name + '.service'], False, True)

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s")
	def disable(self, name):
		logger.verbose("{mod}: Request to disable service \"%s\"" % name)
		self._systemd_manager.DisableUnitFiles([name + '.service'], False, True)

	###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s")
	def reload(self, name) :
		logger.verbose("{mod}: Request to reload service \"%s\"" % name)
		self._systemd_manager.ReloadUnit(name + '.service', 'replace')

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s")
	def start(self, name) :
		logger.verbose("{mod}: Request to start service \"%s\"" % name)
		self._systemd_manager.StartUnit(name + '.service', 'replace')

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s")
	def stop(self, name) :
		logger.verbose("{mod}: Request to stop service \"%s\"" % name)
		self._systemd_manager.StopUnit(name + '.service', 'replace')

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s", out_signature="b")
	def isActive(self, name) :
		unit = DBusInterface(
			self._bus.get_object(
				'org.freedesktop.systemd1',
				str(self._systemd_manager.LoadUnit(name + '.service'))
			),
			'org.freedesktop.systemd1.Unit'
		)
		active_state = unit.Get(
			'org.freedesktop.systemd1.Unit',
			'ActiveState',
			dbus_interface='org.freedesktop.DBus.Properties'
		)
		return active_state == 'active' or active_state == 'reloading'


class Service(service.Service) :
	def initService(self):
		shared.Functions.addSharedObject(SERVICE_NAME, SystemServices(SERVICE_NAME, self))

	@classmethod
	def serviceName(self):
		return SERVICE_NAME
