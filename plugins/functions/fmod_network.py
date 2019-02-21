# -*- coding: utf-8 -*-

import socket
from pyroute2 import IPDB
from pyroute2.netlink.rtnl.ifinfmsg import IFF_UP
from ipaddress import IPv4Address
from yaml import dump

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

import settingsd.tools as tools
import settingsd.tools.process
import settingsd.tools.editors

##### Private constants #####
SERVICE_NAME = "network"

NETWORK_METHODS_NAMESPACE = "network"
NETWORK_SERVICES = {
	'ssh': (22, ),
	'http': (80, 443),
	'smtp': (25, 465, 587)
}


##### Private classes #####
class Network(service.FunctionObject) :
	### DBus methods ###
	@service.functionMethod(NETWORK_METHODS_NAMESPACE, in_signature="s")
	def dumpCurrentSettings(self, filename):
		settings = {}
		settings['hostname'] = socket.gethostname()
		settings['interfaces'] = self._dump_interfaces()
		settings['dns'] = self._get_dns_servers()
		with open(filename, 'w+') as network_config:
			network_config.write(dump(settings))

	def _dump_interfaces(self):
		interfaces = {}

		with IPDB() as ipdb:
			for interface in ipdb.interfaces.values():
				interfaces[interface.ifname] = {
					'enabled': bool(interface.flags & IFF_UP),
					'address': interface.ipaddr[0]['address'],
					'mask': self._prefix_to_netmask(interface.ipaddr[0]['prefixlen']),
					'services': {
						service: False for service in NETWORK_SERVICES
					}
				}
		return interfaces

	def _get_dns_servers(self):
		with open('/etc/resolv.conf', 'r') as resolv_conf:
			return [
				line.split(' ')[1]
				for line in resolv_conf.readlines()
				if line.startswith('nameserver')
			]

	def _prefix_to_netmask(self, prefix):
		return str(IPv4Address(
			(0xffffffff << (32 - prefix)) & 0xffffffff
		))

##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, Network(SERVICE_NAME, self))


	### Private ###
	@classmethod
	def serviceName(self) :
		return SERVICE_NAME
