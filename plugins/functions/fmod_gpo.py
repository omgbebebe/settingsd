# -*- coding: utf-8 -*-


import time

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger
import settingsd.tools as tools

##### Private constants #####
SERVICE_NAME = "gpo"

GPO_METHODS_NAMESPACE = "gpo"

##### Private classes #####
class Gpo(service.FunctionObject) :
	def _update(self, is_machine, who) :
		op = "update"
		target_name = str(who)
		target_type = "machine" if is_machine else "user"
		logger.verbose("{mod}: Update %s`s GPOs for %s" % (target_type, target_name))
		proc_args_list = [config.value(SERVICE_NAME, "gpom"), op, target_type, target_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	def _apply(self, is_machine, who) :
		op = "apply"
		target_name = str(who)
		target_type = "machine" if is_machine else "user"
		logger.verbose("{mod}: Apply %s`s GPOs for %s" % (target_type, target_name))
		proc_args_list = [config.value(SERVICE_NAME, "gpoa"), op, target_type, target_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	### DBus methods ###

	@service.functionMethod(GPO_METHODS_NAMESPACE, out_signature="i", sender_keyword='sender', connection_keyword='conn')
	def update_for_me(self, sender, conn) :
		uid = conn.get_unix_user(sender)
		return self._update(is_machine=False, who=uid)

	@service.functionMethod(GPO_METHODS_NAMESPACE, in_signature="bs", out_signature="i")
	def update(self, is_machine, who) :
		return self._update(is_machine=is_machine, who=who)

	@service.functionMethod(GPO_METHODS_NAMESPACE, out_signature="i", sender_keyword='sender', connection_keyword='conn')
	def apply_for_me(self, sender, conn) :
		uid = conn.get_unix_user(sender)
		return self._apply(is_machine=False, who=uid)

	@service.functionMethod(GPO_METHODS_NAMESPACE, in_signature="bs", out_signature="i")
	def apply(self, is_machine, who) :
		return self._apply(is_machine=is_machine, who=who)

	###


##### Public classes #####
class Service(service.Service) :
	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, Gpo(SERVICE_NAME, self))

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "gpom", "/usr/bin/gpom", str),
			(SERVICE_NAME, "gpoa", "/usr/bin/gpoa", str),
		]

