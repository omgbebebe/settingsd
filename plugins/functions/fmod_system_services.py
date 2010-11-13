# -*- coding: utf-8 -*-


import os
import re
import subprocess

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import dbus_tools
from settingsd import logger
from settingsd import tools
from settingsd import validators


##### Private constants #####
SERVICE_NAME = "system_services"

SYSTEM_SERVICE_METHODS_NAMESPACE = "systemService"

RUNLEVELS = "0123456"


##### Private classes #####
class SystemService(service.FunctionObject) :
	def __init__(self, system_service_name, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__system_service_name = system_service_name


	### DBus methods ###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def on(self, levels = None) :
		return self.setLevels(levels, True)

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def off(self, levels = None) :
		return self.setLevels(levels, False)

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="s")
	def levelsMap(self) :
		proc_args =  "%s --list %s" % (config.value(SERVICE_NAME, "chkconfig_prog_path"), self.systemServiceName())
		(proc_stdout, proc_stderr, proc_returncode) = tools.execProcess(proc_args)

		if proc_returncode != 0 :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		service_record_list = re.split(r"\s+", proc_stdout.split("\n")[0])
		levels_list = ["0"]*(len(service_record_list) - 1)
		for count in xrange(1, len(service_record_list)) :
			(level, state) = service_record_list[count].split(":")
			levels_list[int(level)] = ( "1" if state == "on" else "0" )

		return "".join(levels_list)

	###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="s")
	def shortDescription(self) :
		return "" # TODO: /usr/lib/python2.6/site-packages/scservices/core/servicesinfo.py in RHEL

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="s")
	def description(self) :
		return "" # TODO: /usr/lib/python2.6/site-packages/scservices/core/servicesinfo.py in RHEL

	###

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="i")
	def start(self) :
		logger.verbose("{mod}: Request to start service \"%s\"" % (self.systemServiceName()))
		return tools.execProcess("%s start" % (os.path.join(config.value(SERVICE_NAME, "initd_dir_path"), self.systemServiceName())))[2]

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="i")
	def stop(self) :
		return tools.execProcess("%s stop" % (os.path.join(config.value(SERVICE_NAME, "initd_dir_path"), self.systemServiceName())))[2]
		logger.verbose("{mod}: Request to stop service \"%s\"" % (self.systemServiceName()))

	@service.functionMethod(SYSTEM_SERVICE_METHODS_NAMESPACE, out_signature="i")
	def status(self) :
		return tools.execProcess("%s status" % (os.path.join(config.value(SERVICE_NAME, "initd_dir_path"), self.systemServiceName())))[2]


	### Private ###

	def systemServiceName(self) :
		return self.__system_service_name

	###

	def setLevels(self, levels, enabled_flag) :
		levels = self.validateLevels(levels)

		logger.verbose("Request to %s service \"%s\" on runlevels \"%s\"" % ( ( "enable" if enabled_flag else "disable" ),
			self.systemServiceName(), ( levels if levels != None else "default" ) ))

		proc_args =  "%s %s %s %s" % ( config.value(SERVICE_NAME, "chkconfig_prog_path"), ( "--level %s" % (levels) if levels != None else "" ),
			self.systemServiceName(), ( "on" if enabled_flag else "off" ) )
		(proc_stdout, proc_stderr, proc_returncode) = tools.execProcess(proc_args)

		if proc_returncode != 0 :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		return proc_returncode

	###

	def validateLevels(self, levels) :
		if type(levels).__name__ in ("str", "String") :
			if len(levels) == 0 :
				levels = None
			for level in levels :
				if not level in RUNLEVELS :
					raise validators.ValidatorError("Incorrect item \"%s\" in argument \"%s\"" % (level, levels))
		elif type (levels).__name__ == "NoneType" :
			pass
		else :
			raise validators.ValidatorError("Incorrect type \"%s\" of argument" % (type(levels).__name__))
		return levels


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		proc_args = "%s --list" % (config.value(SERVICE_NAME, "chkconfig_prog_path"))
		(proc_stdout, proc_sterr, proc_returncode) = tools.execProcess(proc_args)

		if proc_returncode != 0 :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		system_service_count = 0
		shared.Functions.addShared(SERVICE_NAME)
		for system_service_record in proc_stdout.split("\n") :
			system_service_record_list = re.split(r"\s+", system_service_record)
			if len(system_service_record_list) != len(RUNLEVELS) + 1 :
				continue

			system_service_name = system_service_record_list[0]
			dbus_system_service_name = re.sub(r"-|\.", "_", system_service_name)
			shared.Functions.shared(SERVICE_NAME).addSharedObject(dbus_system_service_name, SystemService(system_service_name,
				dbus_tools.joinPath(SERVICE_NAME, dbus_system_service_name), self))

			system_service_count += 1
		logger.verbose("{mod}: Added %d system services" % (system_service_count))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "initd_dir_path", "/etc/rc.d/init.d", str),
			(SERVICE_NAME, "chkconfig_prog_path", "/sbin/chkconfig", str)
		]

