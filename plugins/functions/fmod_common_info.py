# -*- coding: utf-8 -*-


from settingsd import config
from settingsd import service
from settingsd import logger
from settingsd import shared

import settingsd.tools as tools


##### Private constants #####
SERVICE_NAME = "common_info"

LSB_RELASE_METHODS_NAMESPACE = "commonInfo.lsbRelease"
UNAME_METHODS_NAMESPACE = "commonInfo.uname"

LSB_OPTION_VERSION = "--version"
LSB_OPTION_ID = "--id"
LSB_OPTION_DESCRIPTION = "--description"
LSB_OPTION_RELEASE = "--release"
LSB_OPTION_CODE_NAME = "--codename"

UNAME_OPTION_KERNEL_NAME = "--kernel-name"
UNAME_OPTION_KERNEL_VERSION = "--kernel-version"
UNAME_OPTION_NODE_NAME = "--nodename"
UNAME_OPTION_RELEASE = "--release"
UNAME_OPTION_MACHINE = "--machine"
UNAME_OPTION_PROCESSOR = "--processor"
UNAME_OPTION_HARDWARE_PLATFORM = "--hardware-platform"
UNAME_OPTION_OPERATING_SYSTEM = "--operating-system"


##### Private classes #####
class CommonInfo(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(LSB_RELASE_METHODS_NAMESPACE, out_signature="s")
	def version(self) :
		return self.lsbOption(LSB_OPTION_VERSION)

	@service.functionMethod(LSB_RELASE_METHODS_NAMESPACE, out_signature="s")
	def id(self) :
		return self.lsbOption(LSB_OPTION_ID)

	@service.functionMethod(LSB_RELASE_METHODS_NAMESPACE, out_signature="s")
	def description(self) :
		return self.lsbOption(LSB_OPTION_DESCRIPTION)

	@service.functionMethod(LSB_RELASE_METHODS_NAMESPACE, out_signature="s")
	def release(self) :
		return self.lsbOption(LSB_OPTION_RELEASE)

	@service.functionMethod(LSB_RELASE_METHODS_NAMESPACE, out_signature="s")
	def codeName(self) :
		return self.lsbOption(LSB_OPTION_CODE_NAME)

	###

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def kernelName(self) :
		return self.unameOption(UNAME_OPTION_KERNEL_NAME)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def kernelVersion(self) :
		return self.unameOption(UNAME_OPTION_KERNEL_VERSION)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def nodeName(self) :
		return self.unameOption(UNAME_OPTION_NODE_NAME)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def release(self) :
		return self.unameOption(UNAME_OPTION_RELEASE)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def machine(self) :
		return self.unameOption(UNAME_OPTION_MACHINE)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def processor(self) :
		return self.unameOption(UNAME_OPTION_PROCESSOR)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def hardwarePlatform(self) :
		return self.unameOption(UNAME_OPTION_HARDWARE_PLATFORM)

	@service.functionMethod(UNAME_METHODS_NAMESPACE, out_signature="s")
	def operatingSystem(self) :
		return self.unameOption(UNAME_OPTION_OPERATING_SYSTEM)


	### Private ###

	def lsbOption(self, option) :
		try:
			proc_args_list = [config.value(SERVICE_NAME, "lsb_release_bin"), option]
			return ":".join(tools.process.execProcess(proc_args_list)[0].split(":")[1:]).strip()
		except FileNotFoundError:
			logger.error("Directory /usr/bin/lsb_release does not exist")
			return "Error: /usr/bin/lsb_release doesn\'t exist"



	def unameOption(self, option) :
		try:
			proc_args_list = [config.value(SERVICE_NAME, "uname_bin"), option]
			return tools.process.execProcess(proc_args_list)[0].strip()
		except FileNotFoundError:
			logger.error("Directory /usr/bin/lsb_release does not exist")
			return "Error: /usr/bin/lsb_release doesn\'t exist"



##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, CommonInfo(SERVICE_NAME, self))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "lsb_release_bin", "/usr/bin/lsb_release", str),
			(SERVICE_NAME, "uname_bin", "/bin/uname", str)
		]

