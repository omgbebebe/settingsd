# -*- coding: utf-8 -*-


import os
import re
import signal
import shutil

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger
from settingsd import validators


##### Private constants #####
SERVICE_NAME = "dnsmasq_config"

SIMPLE_METHODS_NAMESPACE = "dnsmasq.simple"


##### Exceptions #####
class NoDnsmasqProcess(Exception) :
	pass


##### Private classes #####
class SimpleDnsmasqConfig(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, in_signature="as")
	def setServers(self, servers_list) :
		for servers_list_item in servers_list :
			validators.validIpv4Address(servers_list_item)
		self.setConfigValue("server", servers_list)

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, out_signature="as")
	def servers(self) :
		return self.configValue("server")

	###

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, in_signature="as")
	def setInterfaces(self, interfaces_list) :
		self.setConfigValue("interface", interfaces_list)

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, out_signature="as")
	def interfaces(self) :
		return self.configValue("interface")

	##

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, in_signature="as")
	def setExceptInterfaces(self, interfaces_list) :
		self.setConfigValue("except-interface", interfaces_list)

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, out_signature="as")
	def exceptInterfaces(self) :
		return self.configValue("except-interface")

	###

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, in_signature="ssss")
	def setRange(self, start_ip, stop_ip, netmask, lease) :
		dhcp_range = "%s,%s" % (validators.validIpv4Address(start_ip)[0], validators.validIpv4Address(stop_ip)[0])
		dhcp_range += ( ",%s" % (validators.validIpv4Netmask(netmask)[0]) if len(netmask) != 0 else "" )
		dhcp_range += ( ",%s" % (lease) if len(lease) != 0 else "" )
		self.setConfigValue("dhcp-range", dhcp_range)

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, out_signature="ssss")
	def range(self) :
		dhcp_range_list = self.configValue("dhcp-range")
		if len(dhcp_range_list) > 0:
			dhcp_range = dhcp_range_list[-1].split(",")
			dhcp_range += [""] * (4 - len(dhcp_range))
			return dhcp_range
		return [""] * 4

	###

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, in_signature="sss")
	def addStaticHost(self, mac, ip, name) :
		static_host = "%s,%s" % (validators.validMacAddress(mac)[0], validators.validIpv4Address(ip)[0])
		static_host += ( ",%s" % (name) if len(name) != 0 else "" )
		self.setConfigValue("dhcp-host", static_host, False)

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, in_signature="s")
	def removeStaticHost(self, identifier) :
		static_hosts_list = self.configValue("dhcp-host")
		new_static_hosts_list = []
		for static_hosts_list_item in static_hosts_list :
			if not identifier in static_hosts_list_item.split(",") :
				new_static_hosts_list.append(static_hosts_list_item)
		if new_static_hosts_list != static_hosts_list :
			self.setConfigValue("dhcp-host", new_static_hosts_list)

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE, out_signature="a(sss)")
	def staticHosts(self) :
		static_hosts_list = self.configValue("dhcp-host")
		for count in xrange(len(static_hosts_list)) :
			static_host = static_hosts_list[count].split(",")
			static_host += [""] * (3 - len(static_host))
			static_hosts_list[count] = static_host
		return static_hosts_list

	###

	@service.functionMethod(SIMPLE_METHODS_NAMESPACE)
	def reload(self) :
		for proc_list_item in os.listdir("/proc") :
			try :
				proc_pid = int(proc_list_item)
			except :
				continue

			cmdline_file_path = os.path.join("/proc", proc_list_item, "cmdline")
			cmdline_file = open(cmdline_file_path)
			cmdline_list = cmdline_file.read().split("\0")
			try :
				cmdline_file.close()
			except : pass

			if len(cmdline_list) >= 1 and os.path.basename(cmdline_list[0]) == "dnsmasq" :
				os.kill(proc_pid, signal.SIGHUP)
				logger.verbose("{mod}: Sended signal to dnsmasq with pid \"%d\" for re-read configs" % (proc_pid))
				return

		raise NoDnsmasqProcess("Dnsmasq process is not found")


	### Private ###

	def setConfigValue(self, variable_name, values_list, replace_flag = True) :
		if not type(values_list).__name__ in ("list", "tuple") :
			values_list = [values_list]

		dnsmasq_config_file_path = config.value(SERVICE_NAME, "dnsmasq_config_file_path")

		###

		dnsmasq_config_file_path_sample = config.value(SERVICE_NAME, "dnsmasq_config_file_path_sample")
		if not os.access(dnsmasq_config_file_path, os.F_OK) :
			if access(dnsmasq_config_file_path_sample, os.F_OK) :
				shutil.copy2(dnsmasq_config_file_path_sample, dnsmasq_config_file_path)
			else :
				open(dnsmasq_config_file_path, "w").close()

		###

		dnsmasq_config_file = open(dnsmasq_config_file_path, "r+")
		dnsmasq_config_file_data = dnsmasq_config_file.read()

		variable_regexp = re.compile(r"(((\n|\A)%s[\s\t]*=[^\n]*)+)" % (variable_name))
		variable = "\n".join([ "%s=%s" % (variable_name, values_list_item) for values_list_item in values_list ])
		if variable_regexp.search(dnsmasq_config_file_data) :
			if len(variable) != 0 :
				variable = ( "\n" if replace_flag else "\\1\n" )+variable
			dnsmasq_config_file_data = variable_regexp.sub(variable, dnsmasq_config_file_data)
		elif len(variable) != 0 :
			dnsmasq_config_file_data += ( "\n" if dnsmasq_config_file_data[-1] != "\n" else "" )+variable+"\n"

		dnsmasq_config_file.seek(0)
		dnsmasq_config_file.truncate()
		dnsmasq_config_file.write(dnsmasq_config_file_data)

		try :
			dnsmasq_config_file_data.close()
		except : pass

	def configValue(self, variable_name) :
		if os.access(config.value(SERVICE_NAME, "dnsmasq_config_file_path"), os.F_OK) :
			dnsmasq_config_file = open(config.value(SERVICE_NAME, "dnsmasq_config_file_path"), "r")
			dnsmasq_config_file_list = dnsmasq_config_file.read().split("\n")
			try :
				dnsmasq_config_file.close()
			except : pass

			variable_regexp = re.compile(r"^%s[\s\t]*=[\s\t]*([^\n]*)" % (variable_name))
			variables_list = []
			for dnsmasq_config_file_list_item in dnsmasq_config_file_list :
				if len(dnsmasq_config_file_list_item) == 0 :
					continue
				variable_match = variable_regexp.match(dnsmasq_config_file_list_item)
				if variable_match != None :
					variables_list.append(variable_match.group(1))
			return variables_list
		return []



##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, SimpleDnsmasqConfig(SERVICE_NAME, self))


	### Private ###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "dnsmasq_config_file_path", "/etc/dnsmasq.conf", str),

			(SERVICE_NAME, "dnsmasq_config_file_path_sample", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "dnsmasq.conf"), str)
		]

