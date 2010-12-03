# -*- coding: utf-8 -*-


from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger
from settingsd import tools
from settingsd import validators


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
		return tools.execProcess("%s -h now" % (config.value(SERVICE_NAME, "shutdown_prog_path")), False)[2]

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def reboot(self) :
		return tools.execProcess("%s -r now" % (config.value(SERVICE_NAME, "shutdown_prog_path")), False)[2]

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def suspend(self) :
		return tools.execProcess(config.value(SERVICE_NAME, "pm_suspend_prog_path"), False)[2]

	@service.functionMethod(POWER_METHODS_NAMESPACE, out_signature="i")
	def hibernate(self) :
		return tools.execProcess(config.value(SERVICE_NAME, "pm_hibernate_prog_path"), False)[2]

	###

	@service.functionMethod(RUNLEVELS_METHODS_NAMESPACE, in_signature="i", out_signature="i")
	def switchTo(self, level) :
		proc_args = "%s %s" % (config.value(SERVICE_NAME, "telinit_prog_path"), validators.validRange(str(level), RUNLEVELS))
		return tools.execProcess(proc_args, False)[2]

	@service.functionMethod(RUNLEVELS_METHODS_NAMESPACE, out_signature="i")
	def currentLevel(self) :
		proc_args = config.value(SERVICE_NAME, "runlevel_prog_path")

		level_pairs_list = tools.execProcess(proc_args)[0].strip().split(" ")
		if len(level_pairs_list) != 2 or not level_pairs_list[1] in RUNLEVELS :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		return int(level_pairs_list[1])

	@service.functionMethod(RUNLEVELS_METHODS_NAMESPACE, out_signature="i")
	def previousLevel(self) :
		proc_args = config.value(SERVICE_NAME, "runlevel_prog_path")

		level_pairs_list = tools.execProcess(proc_args)[0].strip().split(" ")
		if len(level_pairs_list) != 2 or not level_pairs_list[1] in RUNLEVELS+"N" :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
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
			(SERVICE_NAME, "shutdown_prog_path", "/sbin/shutdown", str),
			(SERVICE_NAME, "pm_suspend_prog_path", "/usr/sbin/pm-suspend", str),
			(SERVICE_NAME, "pm_hibernate_prog_path", "/usr/sbin/pm-hibernate", str),
			(SERVICE_NAME, "telinit_prog_path", "/sbin/telinit", str),
			(SERVICE_NAME, "runlevel_prog_path", "/sbin/runlevel", str)
		]

