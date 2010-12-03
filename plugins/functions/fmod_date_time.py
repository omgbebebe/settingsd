# -*- coding: utf-8 -*-


import os
import time
import re
import hashlib

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import tools

##### Private constants #####
SERVICE_NAME = "date_time"

SYSTEM_CLOCK_METHODS_NAMESPACE = "time.systemClock"
HARDWARE_CLOCK_METHODS_NAMESPACE = "time.hardwareClock"
ZONE_METHODS_NAMESPACE = "time.zone"


##### Exceptions #####
class InvalidTimeZone(Exception) :
	pass


##### Private classes #####
class DateTime(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(SYSTEM_CLOCK_METHODS_NAMESPACE, in_signature="iiiiii", out_signature="i")
	def setUtcTime(self, month, monthday, hour, minute, year, second) :
		proc_args = "%s -u %02d%02d%02d%02d%04d.%02d" % ( config.value(SERVICE_NAME, "date_prog_path"),
			month, monthday, hour, minute, year, second )
		return tools.execProcess(proc_args, False)[2]

	@service.functionMethod(SYSTEM_CLOCK_METHODS_NAMESPACE, out_signature="iiiiii")
	def utcTime(self) :
		gm_time = time.gmtime()
		return (gm_time.tm_mon, gm_time.tm_mday, gm_time.tm_hour, gm_time.tm_min, gm_time.tm_year, gm_time.tm_sec)

	###

	@service.functionMethod(ZONE_METHODS_NAMESPACE, in_signature="s")
	def setTimeZone(self, zone) :
		if not os.access(os.path.join(config.value(SERVICE_NAME, "zoneinfo_dir_path"), zone), os.F_OK) :
			raise InvalidTimeZone("Unknown time zone \"%s\"" % (zone))

		os.remove(config.value(SERVICE_NAME, "localtime_file_path"))
		os.symlink(os.path.join(config.value(SERVICE_NAME, "zoneinfo_dir_path"), zone),
			config.value(SERVICE_NAME, "localtime_file_path"))

		if not os.access(config.value(SERVICE_NAME, "clock_config_file_path"), os.F_OK) :
			open(config.value(SERVICE_NAME, "clock_config_file_path"), "w").close()

		clock_config_file = open(config.value(SERVICE_NAME, "clock_config_file_path"), "r+")
		clock_config_file_data = clock_config_file.read()

		clock_config_file_data = re.sub(r"(\A|\n)ZONE=[\"\']?[a-zA-Z0-9/]*[\"\']?", "\nZONE=\"%s\"" % (zone), clock_config_file_data)

		clock_config_file.seek(0)
		clock_config_file.truncate()
		clock_config_file.write(clock_config_file_data)

		try :
			clock_config_file.close()
		except : pass

	@service.functionMethod(ZONE_METHODS_NAMESPACE, out_signature="s")
	def timeZone(self) :
		if os.access(config.value(SERVICE_NAME, "clock_config_file_path"), os.F_OK) :
			clock_config_file = open(config.value(SERVICE_NAME, "clock_config_file_path"))
			clock_config_file_data = clock_config_file.read()
			try :
				clock_config_file.close()
			except : pass

			zone_match = re.search(r"(\A|\n)ZONE=[\"\']?([a-zA-Z0-9/]*)[\"\']?", clock_config_file_data)
			if zone_match != None :
				return os.path.normpath(zone_match.group(2))

		try :
			zoneinfo_dir_path = os.path.normpath(os.readlink(config.value(SERVICE_NAME, "localtime_file_path")))
		except :
			zoneinfo_cache_dict = {}
			for (root_dir_path, dirs_list, files_list) in os.walk(config.value(SERVICE_NAME, "zoneinfo_dir_path")) :
				for files_list_item in files_list :
					zone_file_path = os.path.normpath(os.path.join(root_dir_path, files_list_item))
					zone_file = open(zone_file_path)
					zoneinfo_cache_dict[hashlib.sha1(zone_file.read()).hexdigest()] = zone_file_path
					try :
						zone_file.close()
					except : pass

			zone_file = open(config.value(SERVICE_NAME, "localtime_file_path"))
			zone_file_hash = hashlib.sha1(zone_file.read()).hexdigest()
			try :
				zone_file.close()
			except : pass

			zoneinfo_dir_path = ( zoneinfo_cache_dict[zone_file_hash] if zoneinfo_cache_dict.has_key(zone_file_hash) else "" )

		zoneinfo_dir_path_regexp_str = r"^%s/+(.*)" % (config.value(SERVICE_NAME, "zoneinfo_dir_path"))
		return os.path.normpath(re.sub(zoneinfo_dir_path_regexp_str, r"\1", zoneinfo_dir_path))

	###

	@service.functionMethod(HARDWARE_CLOCK_METHODS_NAMESPACE, out_signature="i")
	def syncWithSystem(self) :
		return tools.execProcess("%s --systohc" % (config.value(SERVICE_NAME, "hwclock_prog_path")), False)[0]


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, DateTime(SERVICE_NAME, self))


	### Private ###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "date_prog_path", "/bin/date", str),
			(SERVICE_NAME, "hwclock_prog_path", "/usr/sbin/hwclock", str),
			(SERVICE_NAME, "localtime_file_path", "/etc/localtime", str),
			(SERVICE_NAME, "zoneinfo_dir_path", "/usr/share/zoneinfo", str),
			(SERVICE_NAME, "clock_config_file_path", "/etc/sysconfig/clock", str)
		]

