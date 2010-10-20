# -*- coding: utf-8 -*-


import subprocess

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger


##### Private constants #####
SERVICE_NAME = "common_info"

LSB_RELASE_METHODS_NAMESPACE = "commonInfo.lsb.release"
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


##### Exceptions #####
class SubprocessFailure(Exception) :
	pass


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
		proc_args = "%s %s" % (config.value(SERVICE_NAME, "lsb_release_prog_path"), option)
		(proc_stdout, proc_stderr, proc_returncode) = self.execProcess(proc_args)

		if proc_returncode != 0 :
			raise SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		return ":".join(proc_stdout.split(":")[1:]).strip()

	def unameOption(self, option) :
		proc_args = "%s %s" % (config.value(SERVICE_NAME, "uname_prog_path"), option)
		(proc_stdout, proc_stderr, proc_returncode) = self.execProcess(proc_args)

		if proc_returncode != 0 :
			raise SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		return proc_stdout.strip()

	###

	def execProcess(self, proc_args) :
		logger.debug("{mod}: Executing child process \"%s\"" % (proc_args))
		proc = subprocess.Popen(proc_args, shell=True, bufsize=1024, close_fds=True,
			stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
			env={ "LC_ALL" : "C" })
		(proc_stdout, proc_stderr) = proc.communicate()
		logger.debug("{mod}: Child process \"%s\" finished, return_code=%d" % (proc_args, proc.returncode))

		return (proc_stdout, proc_stderr, proc.returncode)


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
			(SERVICE_NAME, "lsb_release_prog_path", "/usr/bin/lsb_release", str),
			(SERVICE_NAME, "uname_prog_path", "/bin/uname", str)
		]

