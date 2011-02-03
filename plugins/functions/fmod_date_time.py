# -*- coding: utf-8 -*-


import os
import time
import re
import hashlib
import shutil

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared

import settingsd.tools as tools
import settingsd.tools.process
import settingsd.tools.editors


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
		proc_args = "%s -u %02d%02d%02d%02d%04d.%02d" % ( config.value(SERVICE_NAME, "date_bin"),
			month, monthday, hour, minute, year, second )
		return tools.process.execProcess(proc_args, False)[2]

	@service.functionMethod(SYSTEM_CLOCK_METHODS_NAMESPACE, out_signature="iiiiii")
	def utcTime(self) :
		gm_time = time.gmtime()
		return (gm_time.tm_mon, gm_time.tm_mday, gm_time.tm_hour, gm_time.tm_min, gm_time.tm_year, gm_time.tm_sec)

	###

	@service.functionMethod(ZONE_METHODS_NAMESPACE, in_signature="s")
	def setTimeZone(self, zone) :
		if not os.access(os.path.join(config.value(SERVICE_NAME, "zoneinfo_dir"), zone), os.F_OK) :
			raise InvalidTimeZone("Unknown time zone \"%s\"" % (zone))

		os.remove(config.value(SERVICE_NAME, "localtime_file"))
		os.symlink(os.path.join(config.value(SERVICE_NAME, "zoneinfo_dir"), zone),
			config.value(SERVICE_NAME, "localtime_file"))

		time_zone_editor = tools.editors.PlainEditor(spaces_list=[])
		time_zone_editor.open(config.value(SERVICE_NAME, "clock_conf"),
			config.value(SERVICE_NAME, "clock_conf_sample"))
		time_zone_editor.setValue("ZONE", zone)
		time_zone_editor.save()
		time_zone_editor.close()

	@service.functionMethod(ZONE_METHODS_NAMESPACE, out_signature="s")
	def timeZone(self) :
		if os.access(config.value(SERVICE_NAME, "clock_conf"), os.F_OK) :
			time_zone_editor = tools.editors.PlainEditor(spaces_list=[])
			time_zone_editor.open(config.value(SERVICE_NAME, "clock_conf"))
			zones_list = time_zone_editor.value("ZONE")
			time_zone_editor.close()
			if len(zones_list) > 0 :
				return os.path.normpath(zones_list[-1])

		try :
			zoneinfo_dir_path = os.path.normpath(os.readlink(config.value(SERVICE_NAME, "localtime_file")))
		except :
			zoneinfo_cache_dict = {}
			for (root_dir_path, dirs_list, files_list) in os.walk(config.value(SERVICE_NAME, "zoneinfo_dir")) :
				for files_list_item in files_list :
					zone_file_path = os.path.normpath(os.path.join(root_dir_path, files_list_item))
					zone_file = open(zone_file_path)
					zoneinfo_cache_dict[hashlib.sha1(zone_file.read()).hexdigest()] = zone_file_path
					try :
						zone_file.close()
					except : pass

			zone_file = open(config.value(SERVICE_NAME, "localtime_file"))
			zone_file_hash = hashlib.sha1(zone_file.read()).hexdigest()
			try :
				zone_file.close()
			except : pass

			zoneinfo_dir_path = ( zoneinfo_cache_dict[zone_file_hash] if zoneinfo_cache_dict.has_key(zone_file_hash) else "" )

		zoneinfo_dir_path_regexp_str = r"^%s/+(.*)" % (config.value(SERVICE_NAME, "zoneinfo_dir"))
		return os.path.normpath(re.sub(zoneinfo_dir_path_regexp_str, r"\1", zoneinfo_dir_path))

	###

	@service.functionMethod(HARDWARE_CLOCK_METHODS_NAMESPACE, out_signature="i")
	def syncWithSystem(self) :
		return tools.process.execProcess("%s --systohc" % (config.value(SERVICE_NAME, "hwclock_bin")), False)[0]


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
			(SERVICE_NAME, "date_bin", "/bin/date", str),
			(SERVICE_NAME, "hwclock_bin", "/usr/sbin/hwclock", str),
			(SERVICE_NAME, "localtime_file", "/etc/localtime", str),
			(SERVICE_NAME, "zoneinfo_dir", "/usr/share/zoneinfo", str),
			(SERVICE_NAME, "clock_conf", "/etc/sysconfig/clock", str),

			(SERVICE_NAME, "clock_conf_sample", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "clock"), str)
		]

