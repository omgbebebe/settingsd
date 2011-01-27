# -*- coding: utf-8 -*-


import os
import re
import shutil

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

import settingsd.tools as tools
import settingsd.tools.process
import settingsd.tools.editors

##### Private constants #####
SERVICE_NAME = "ntp_config"

NTP_METHODS_NAMESPACE = "time.ntp"


##### Private classes #####
class NtpConfig(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(NTP_METHODS_NAMESPACE, in_signature="as")
	def setServers(self, servers_list) :
		ntp_editor = tools.editors.PlainEditor(delimiter = "", quotes_list = [])
		ntp_editor.open(config.value(SERVICE_NAME, "ntp_config_file_path"),
			config.value(SERVICE_NAME, "sample_ntp_config_file_path"))
		ntp_editor.setValue("server", servers_list)
		ntp_editor.save()
		ntp_editor.close()

	@service.functionMethod(NTP_METHODS_NAMESPACE, out_signature="as")
	def servers(self) :
		ntp_editor = tools.editors.PlainEditor(delimiter = "", quotes_list = [])
		ntp_editor.open(config.value(SERVICE_NAME, "ntp_config_file_path"))
		servers_list = ntp_editor.value("server")
		ntp_editor.close()
		return servers_list

	###

	@service.functionMethod(NTP_METHODS_NAMESPACE)
	def request(self) :
		proc_args =  "%s %s" % (config.value(SERVICE_NAME, "ntpdate_prog_path"), " ".join(self.servers()))
		tools.process.execProcess(proc_args)


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, NtpConfig(SERVICE_NAME, self))


	### Private ###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "ntpdate_prog_path", "/usr/sbin/ntpdate", str),
			(SERVICE_NAME, "ntp_config_file_path", "/etc/ntp.conf", str),

			(SERVICE_NAME, "sample_ntp_config_file_path", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "ntp.conf"), str)
		]

