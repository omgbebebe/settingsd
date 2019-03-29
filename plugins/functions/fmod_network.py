# -*- coding: utf-8 -*-

import socket
import os
from pyroute2 import IPDB
from pyroute2.netlink.rtnl.ifinfmsg import IFF_UP
from ipaddress import IPv4Address
from yaml import dump, safe_load

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

import settingsd.tools as tools
from settingsd.tools.process import execProcess
import settingsd.tools.editors

from jinja2 import Template

##### Private constants #####
SERVICE_NAME = "network"

NETWORK_METHODS_NAMESPACE = "network"
NETWORK_SERVICES = {
	'ssh': (22, ),
	'http': (80, 443),
	'smtp': (25, 465, 587)
}
NFTABLES_CONFIG_FILE = '/etc/nftables.conf'
# jinja2
NFTABLES_CONFIG_TEMPLATE = Template('''#!/usr/sbin/nft -f
flush ruleset

table ip filter {
	chain input {
		type filter hook input priority 0;
		{% for name in interfaces -%}
		iifname {{name}} jump input_{{name}}
		{% endfor -%}
		reject with icmp type port-unreachable
	}
	{%- for name in interfaces %}
	chain input_{{name}} {
		ct state {established,related} accept
		{% for port in interfaces[name] -%}
		tcp dport {{port}} {{ 'accept' if interfaces[name][port] else 'drop' }}
		{% endfor -%}
		{{ 'accept' if name == 'lo' else 'drop' }}
	}
	{%- endfor %}
}
''')


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

	@service.functionMethod(NETWORK_METHODS_NAMESPACE, out_signature='a{sa{st}}')
	def getStatistics(self):
		with IPDB() as ipdb:
			interfaces = [i.ifname for i in ipdb.interfaces.values()]
		
		stats = {}

		for interface_name in interfaces:
			with open('/sys/class/net/' + interface_name + '/statistics/rx_bytes', 'r') as file:
				rx = int(file.read())
			with open('/sys/class/net/' + interface_name + '/statistics/tx_bytes', 'r') as file:
				tx = int(file.read())

			stats[interface_name] = {
				'rx': rx,
				'tx': tx
			}

		return stats

	@service.functionMethod(NETWORK_METHODS_NAMESPACE, in_signature="s")
	def reloadNetworkConfig(self, filename):
		with open(filename, 'r') as network_config:
			settings = safe_load(network_config.read())
		if settings.get('hostname') is not None:
			self._set_hostname(settings['hostname'])
		
		if settings.get('dns') is not None:
			self._set_dns_servers(settings['dns'])

		if settings.get('interfaces') is not None:
			self._apply_interface_settings(settings['interfaces'])

	def _apply_interface_settings(self, interface_settings):
		with IPDB() as ipdb:
			interfaces = [i.ifname for i in ipdb.interfaces.values()]

		port_settings = {}
		
		for key in interfaces:
			port_settings[key] = self._get_port_settings(interface_settings, key)

		self._generate_nftables_config(port_settings)	

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

	def _generate_nftables_config(self, settings):
		config = NFTABLES_CONFIG_TEMPLATE.render(interfaces=settings)

		with open(NFTABLES_CONFIG_FILE, 'w+') as config_file:
			config_file.write(config)
	
	def _get_port_settings(self, interface_settings, key):
		settings = {}
		if interface_settings.get(key) is not None:
			for service in NETWORK_SERVICES:
				if not service in NETWORK_SERVICES:
					continue
				for port in NETWORK_SERVICES[service]:
					settings[port] = interface_settings[key]['services'].get(service) or False
		else:
			# if not set, ban everything
			for service, ports in NETWORK_SERVICES.items():
				for port in ports:
					settings[port] = False
		return settings

	def _get_dns_servers(self):
		with open('/etc/resolv.conf', 'r') as resolv_conf:
			return [
				line.strip().split(' ')[1]
				for line in resolv_conf.read().splitlines()
				if line.strip().startswith('nameserver')
			]

	def _prefix_to_netmask(self, prefix):
		return str(IPv4Address(
			(0xffffffff << (32 - prefix)) & 0xffffffff
		))

	def _set_dns_servers(self, dns_list):
		with open('/etc/resolv.conf', 'r+') as resolv_conf:
			lines = [
				line for line in resolv_conf.read().splitlines()
				if not line.strip().startswith('nameserver')
			]
			lines += ['nameserver ' + dns for dns in dns_list]
			resolv_conf.seek(0, os.SEEK_SET)
			resolv_conf.write('\n'.join(lines))
			resolv_conf.truncate()

	def _set_hostname(self, hostname):
		with open('/etc/hostname', 'w') as etc_hostname:
			etc_hostname.write(hostname)
		execProcess(['hostname', hostname], shell=True)

##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, Network(SERVICE_NAME, self))


	### Private ###
	@classmethod
	def serviceName(self) :
		return SERVICE_NAME
