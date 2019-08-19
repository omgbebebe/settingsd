# -*- coding: utf-8 -*-


import time
import threading

import subprocess
import dbus, dbus.service
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger
import settingsd.tools as tools

SERVICE_ROOT_NAME="org.etersoft.settingsd"
SERVICE_FULL_NAME="org.etersoft.settingsd.functions.gpo"
SERVICE_FULL_PATH="/" + SERVICE_FULL_NAME.replace('.', '/')
##### Private constants #####
SERVICE_NAME = "gpo"

GPO_METHODS_NAMESPACE = "gpo"

def mk_long_run(operation, session_id, proc_args_list):
	event_name = "{}_{}".format(operation, session_id)

	class LongRun(dbus.service.Object):
		def __init__(self):
			self.busName = dbus.service.BusName(SERVICE_ROOT_NAME, bus=dbus.SystemBus())
			dbus.service.Object.__init__(self, self.busName, SERVICE_FULL_PATH + '/' + event_name)
			self.thread = threading.Thread(target=self.work)
			self.thread.start()
			self.thread_id = str(self.thread.ident)

		def work(self):
			env = { "LC_ALL" : "C" }
			shell = False
			proc = subprocess.Popen(proc_args_list, bufsize=1024, close_fds=True,
					stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
					env=env, shell=shell)

			while proc.poll() == None:
				l = proc.stderr.readline()
				self.progress(l)

			self.done(proc.returncode)
			self.remove_from_connection(None, SERVICE_FULL_PATH + '/' + event_name)

		@dbus.service.signal(dbus_interface=SERVICE_FULL_NAME + '.' + event_name, signature='s')
		def progress(self, data):
			pass
#            print("In {} event, got: {}".format(event_name, data))

		@dbus.service.signal(dbus_interface=SERVICE_FULL_NAME + '.' + event_name, signature='i')
		def done(self, returncode):
			pass

	return LongRun()


##### Private classes #####
class Gpo(service.FunctionObject) :
	def _update(self, is_machine, who, session_id) :
		op = "update"
		target_name = str(who)
		target_type = "machine" if is_machine else "user"
		logger.verbose("{mod}: Update %s`s GPOs for %s" % (target_type, target_name))
		proc_args_list = [config.value(SERVICE_NAME, "gpom"), op, target_type, target_name]
		mk_long_run("update_{target}_{id}".format(target='machine' if is_machine else 'user',id=who), session_id, proc_args_list)
		return 0
#		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	def _apply(self, is_machine, who, session_id) :
		op = "apply"
		target_name = str(who)
		target_type = "machine" if is_machine else "user"
		logger.verbose("{mod}: Apply %s`s GPOs for %s" % (target_type, target_name))
		proc_args_list = [config.value(SERVICE_NAME, "gpoa"), op, target_type, target_name]
		mk_long_run("apply_{target}_{id}".format(target='machine' if is_machine else 'user', id=who), session_id, proc_args_list)
		return 0
#		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	### DBus methods ###

	@service.functionMethod(GPO_METHODS_NAMESPACE, in_signature="s", out_signature="i", sender_keyword='sender', connection_keyword='conn')
	def update_for_me(self, session_id, sender, conn) :
		uid = conn.get_unix_user(sender)
		return self._update(is_machine=False, who=uid, session_id=session_id)

	@service.functionMethod(GPO_METHODS_NAMESPACE, in_signature="sbs", out_signature="i")
	def update(self, session_id, is_machine, who) :
		return self._update(is_machine=is_machine, who=who, session_id=session_id)

	@service.functionMethod(GPO_METHODS_NAMESPACE, in_signature="s", out_signature="i", sender_keyword='sender', connection_keyword='conn')
	def apply_for_me(self, session_id, sender, conn) :
		uid = conn.get_unix_user(sender)
		return self._apply(is_machine=False, who=uid, session_id=session_id)

	@service.functionMethod(GPO_METHODS_NAMESPACE, in_signature="sbs", out_signature="i")
	def apply(self, session_id, is_machine, who) :
		return self._apply(is_machine=is_machine, who=who, session_id=session_id)

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

