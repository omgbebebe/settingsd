# -*- coding: utf-8 -*-


import re

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
		ntp_config_file = open(config.value(SERVICE_NAME, "ntp_config_file_path"), "r+")
		ntp_config_file_data = ntp_config_file.read()

		ntp_config_file_data = re.sub(r"\nserver[\s\t]+[^\n]+", "", ntp_config_file_data)
		for servers_list_item in servers_list :
			ntp_config_file_data += "server %s\n" % (servers_list_item)

		ntp_config_file.seek(0)
		ntp_config_file.truncate()
		ntp_config_file.write(ntp_config_file_data)

		try :
			ntp_config_file.close()
		except : pass

	@service.functionMethod(NTP_METHODS_NAMESPACE, out_signature="as")
	def servers(self) :
		ntp_config_file = open(config.value(SERVICE_NAME, "ntp_config_file_path"), "r")
		ntp_config_file_list = ntp_config_file.read().split("\n")
		try :
			ntp_config_file.close()
		except : pass

		servers_list = []
		for ntp_config_file_list_item in ntp_config_file_list :
			if len(ntp_config_file_list_item) == 0 :
				continue
			if re.match(r"^server[\s\t]+", ntp_config_file_list_item) != None :
				servers_list.append(re.split(r"[\s\t]+", ntp_config_file_list_item)[1])
		return servers_list

	###

	@service.functionMethod(NTP_METHODS_NAMESPACE)
	def request(self) :
		proc_args =  "%s %s" % (config.value(SERVICE_NAME, "ntpdate_prog_path"), " ".join(self.servers()))
		tools.execProcess(proc_args)


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
			(SERVICE_NAME, "ntp_config_file_path", "/etc/ntp.conf", str)
		]

