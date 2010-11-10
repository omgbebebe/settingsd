# -*- coding: utf-8 -*-


import re
import subprocess

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger


##### Private constants #####
SERVICE_NAME = "ntp_config"

NTP_METHODS_NAMESPACE = "time.ntp"


##### Exceptions #####
class SubprocessFailure(Exception) :
	pass


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
		(proc_stdout, proc_stderr, proc_returncode) = self.execProcess(proc_args)

		if proc_returncode != 0 :
			raise SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))


	### Private ###

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

