import os
import re
from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd.tools.process import execProcess


INTERFACE_NAME = "packageUpdates"
SERVICE_NAME = "package_updates"
APT_EXECUTABLE = "/usr/bin/apt"
PACKAGE_REGEX = re.compile(r'^(\S+)/\S+')


class PackageUpdates(service.FunctionObject) :
	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="as")
	def get_available_updates(self):
		execProcess([APT_EXECUTABLE, 'update'])
		raw_output, = execProcess([APT_EXECUTABLE, 'list', '--upgradable'])[:1]
		return self._extract_upgradable_packages(raw_output.decode('utf-8'))
	
	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="")
	def install_updates(self):
		execProcess([APT_EXECUTABLE, 'upgrade', '-y'], shell=True, inherit_env=True)

	def _extract_upgradable_packages(self, apt_output):
		lines = apt_output.split('\n')
		matches = [PACKAGE_REGEX.match(line) for line in lines]
		return [m[1] for m in matches if m]


class Service(service.Service) :
	def initService(self):
		shared.Functions.addSharedObject(SERVICE_NAME, PackageUpdates(SERVICE_NAME, self))

	@classmethod
	def serviceName(self):
		return SERVICE_NAME
