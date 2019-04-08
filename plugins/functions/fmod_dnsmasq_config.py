# -*- coding: utf-8 -*-


import os
import signal

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

import settingsd.validators as validators

import settingsd.tools as tools


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
			validators.network.validIpv4Address(servers_list_item)
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
		dhcp_range = "%s,%s" % (validators.network.validIpv4Address(start_ip)[0], validators.network.validIpv4Address(stop_ip)[0])
		dhcp_range += ( ",%s" % (validators.network.validIpv4Netmask(netmask)[0]) if len(netmask) != 0 else "" )
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
		static_host = "%s,%s" % (validators.network.validMacAddress(mac)[0], validators.network.validIpv4Address(ip)[0])
		static_host += ( ",%s" % (name) if len(name) != 0 else "" )

		dnsmasq_editor = tools.editors.PlainEditor(spaces_list = [], quotes_list = [])
		dnsmasq_editor.open(config.value(SERVICE_NAME, "dnsmasq_conf"),
			config.value(SERVICE_NAME, "dnsmasq_conf_sample"))
		dnsmasq_editor.setValue("dhcp-host", dnsmasq_editor.value("dhcp_host") + [static_host])
		dnsmasq_editor.save()
		dnsmasq_editor.close()

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

	def setConfigValue(self, variable_name, values_list) :
		dnsmasq_editor = tools.editors.PlainEditor(spaces_list = [], quotes_list = [])
		dnsmasq_editor.open(config.value(SERVICE_NAME, "dnsmasq_conf"),
			config.value(SERVICE_NAME, "dnsmasq_conf_sample"))
		dnsmasq_editor.setValue(variable_name, values_list)
		dnsmasq_editor.save()
		dnsmasq_editor.close()

	def configValue(self, variable_name) :
		dnsmasq_editor = tools.editors.PlainEditor(spaces_list = [], quotes_list = [])
		dnsmasq_editor.open(config.value(SERVICE_NAME, "dnsmasq_conf"))
		values_list = dnsmasq_editor.value(variable_name)
		dnsmasq_editor.close()
		return values_list


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
			(SERVICE_NAME, "dnsmasq_conf", "/etc/dnsmasq.conf", str),

			(SERVICE_NAME, "dnsmasq_conf_sample", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "dnsmasq.conf"), str)
		]

