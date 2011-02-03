# -*- coding: utf-8 -*-


from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

import settingsd.tools as tools
import settingsd.tools.process

import settingsd.validators as validators
import settingsd.validators.common


##### Private constants #####
SERVICE_NAME = "machine"

POWER_METHODS_NAMESPACE = "power"
RUNLEVELS_METHODS_NAMESPACE = "runlevels"

RUNLEVELS = "0123456"


##### Private classes #####
class Machine(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def shutdown(self) :
		return tools.process.execProcess("%s -h now" % (config.value(SERVICE_NAME, "shutdown_bin")), False)[2]

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def reboot(self) :
		return tools.process.execProcess("%s -r now" % (config.value(SERVICE_NAME, "shutdown_bin")), False)[2]

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def suspend(self) :
		return tools.process.execProcess(config.value(SERVICE_NAME, "pm_suspend_bin"), False)[2]

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def hibernate(self) :
		return tools.process.execProcess(config.value(SERVICE_NAME, "pm_hibernate_bin"), False)[2]

	###

	@service.functionMethod(RUNLEVELS_METHODS_NAMESPACE, in_signature="i", out_signature="i")
	def switchTo(self, level) :
		proc_args = "%s %s" % (config.value(SERVICE_NAME, "telinit_bin"), validators.common.validRange(str(level), RUNLEVELS))
		return tools.process.execProcess(proc_args, False)[2]

	@service.functionMethod(RUNLEVELS_METHODS_NAMESPACE, out_signature="i")
	def currentLevel(self) :
		proc_args = config.value(SERVICE_NAME, "runlevel_bin")

		level_pairs_list = tools.process.execProcess(proc_args)[0].strip().split(" ")
		if len(level_pairs_list) != 2 or not level_pairs_list[1] in RUNLEVELS :
			raise tools.process.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		return int(level_pairs_list[1])

	@service.functionMethod(RUNLEVELS_METHODS_NAMESPACE, out_signature="i")
	def previousLevel(self) :
		proc_args = config.value(SERVICE_NAME, "runlevel_bin")

		level_pairs_list = tools.process.execProcess(proc_args)[0].strip().split(" ")
		if len(level_pairs_list) != 2 or not level_pairs_list[1] in RUNLEVELS+"N" :
			raise tools.process.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		return ( int(level_pairs_list[0]) if level_pairs_list[0] in RUNLEVELS else -1 )


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, Machine(SERVICE_NAME, self))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "shutdown_bin", "/sbin/shutdown", str),
			(SERVICE_NAME, "pm_suspend_bin", "/usr/sbin/pm-suspend", str),
			(SERVICE_NAME, "pm_hibernate_bin", "/usr/sbin/pm-hibernate", str),
			(SERVICE_NAME, "telinit_bin", "/sbin/telinit", str),
			(SERVICE_NAME, "runlevel_bin", "/sbin/runlevel", str)
		]

