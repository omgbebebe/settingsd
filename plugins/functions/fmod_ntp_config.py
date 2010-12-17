# -*- coding: utf-8 -*-


import os
import re
import shutil

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger
from settingsd import tools


##### Private constants #####
SERVICE_NAME = "ntp_config"

NTP_METHODS_NAMESPACE = "time.ntp"


##### Private classes #####
class NtpConfig(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(NTP_METHODS_NAMESPACE, in_signature="as")
	def setServers(self, servers_list) :
		self.setConfigValue("server", servers_list)

	@service.functionMethod(NTP_METHODS_NAMESPACE, out_signature="as")
	def servers(self) :
		return self.configValue("server")

	###

	@service.functionMethod(NTP_METHODS_NAMESPACE)
	def request(self) :
		proc_args =  "%s %s" % (config.value(SERVICE_NAME, "ntpdate_prog_path"), " ".join(self.servers()))
		tools.execProcess(proc_args)


	### Private ###

	def setConfigValue(self, variable_name, values_list, replace_flag = True) :
		if not type(values_list).__name__ in ("list", "tuple") :
			values_list = [values_list]

		ntp_config_file_path = config.value(SERVICE_NAME, "ntp_config_file_path")

		###

		ntp_config_file_path_sample = config.value(SERVICE_NAME, "ntp_config_file_path_sample")
		if not os.access(ntp_config_file_path, os.F_OK) :
			if os.access(ntp_config_file_path_sample, os.F_OK) :
				shutil.copy2(ntp_config_file_path_sample, ntp_config_file_path)
			else :
				open(ntp_config_file_path, "w").close()

		###

		ntp_config_file = open(ntp_config_file_path, "r+")
		ntp_config_file_data = ntp_config_file.read()

		variable_regexp = re.compile(r"(((\n|\A)%s[\s\t]+[^\n]*)+)" % (variable_name))
		variable = "\n".join([ "%s %s" % (variable_name, values_list_item) for values_list_item in values_list ])
		if variable_regexp.search(ntp_config_file_data) :
			if len(variable) != 0 :
				variable = ( "\n" if replace_flag else "\\1\n" )+variable
			ntp_config_file_data = variable_regexp.sub(variable, ntp_config_file_data)
		elif len(variable) != 0 :
			ntp_config_file_data += ( "\n" if ntp_config_file_data[-1] != "\n" else "" )+variable+"\n"

		ntp_config_file.seek(0)
		ntp_config_file.truncate()
		ntp_config_file.write(ntp_config_file_data)

		try :
			ntp_config_file_data.close()
		except : pass

	def configValue(self, variable_name) :
		if os.access(config.value(SERVICE_NAME, "ntp_config_file_path"), os.F_OK) :
			ntp_config_file = open(config.value(SERVICE_NAME, "ntp_config_file_path"), "r")
			ntp_config_file_list = ntp_config_file.read().split("\n")
			try :
				ntp_config_file.close()
			except : pass

			variable_regexp = re.compile(r"^%s[\s\t]+([^\n]*)" % (variable_name))
			variables_list = []
			for ntp_config_file_list_item in ntp_config_file_list :
				if len(ntp_config_file_list_item) == 0 :
					continue
				variable_match = variable_regexp.match(ntp_config_file_list_item)
				if variable_match != None :
					variables_list.append(variable_match.group(1))
			return variables_list
		return []




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

			(SERVICE_NAME, "ntp_config_file_path_sample", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "ntp.conf"), str)
		]

