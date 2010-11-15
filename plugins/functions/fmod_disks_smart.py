# -*- coding: utf-8 -*-


import os
import re
import gudev
import glib

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import dbus_tools
from settingsd import tools
from settingsd import logger


##### Private constants #####
SERVICE_NAME = "disks_smart"

DISKS_SMART_SHARED_NAME = "disks_smart"

DISKS_SMART_OBJECT_NAME = "disks_smart"

SMART_METHODS_NAMESPACE = "disks.smart"


##### Private classes #####
class Disk(service.FunctionObject) :
	def __init__(self, device_path, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__device_path = device_path


	### DBus methods ###

	@service.functionMethod(SMART_METHODS_NAMESPACE, out_signature="a(isiiiissss)")
	def attributes(self) :
		proc_args = "%s -A %s" % (config.value(SERVICE_NAME, "smartctl_prog_path"), self.__device_path)
		(proc_stdout, proc_stderr, proc_returncode) = tools.execProcess(proc_args)

		if proc_returncode != 0 :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		attrs_list = []
		attrs_found_flag = False
		for attrs_list_item in proc_stdout.split("\n") :
			attrs_list_item = attrs_list_item.strip()

			if attrs_found_flag :
				attrs_records_list = re.split(r"\s+", attrs_list_item)
				if len(attrs_records_list) == 10 and attrs_records_list[0] != "ID#" :
					attrs_list.append([int(attrs_records_list[0]),
						attrs_records_list[1],
						int(attrs_records_list[2], 16),
						int(attrs_records_list[3]),
						int(attrs_records_list[4]),
						int(attrs_records_list[5]),
						attrs_records_list[6],
						attrs_records_list[7],
						attrs_records_list[8],
						attrs_records_list[9]])

			if attrs_list_item == "=== START OF READ SMART DATA SECTION ===" :
				attrs_found_flag = True
		return attrs_list

	@service.functionMethod(SMART_METHODS_NAMESPACE, out_signature="b")
	def health(self) :
		proc_args = "%s -H %s" % (config.value(SERVICE_NAME, "smartctl_prog_path"), self.__device_path)
		(proc_stdout, proc_stderr, proc_returncode) = tools.execProcess(proc_args)

		if proc_returncode != 0 :
			raise tools.SubprocessFailure("Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
				proc_args, proc_stdout.strip(), proc_stderr.strip(), proc_returncode ))

		disk_health_flag = False
		health_found_flag = False
		for health_list_item in proc_stdout.split("\n") :
			health_list_item = health_list_item.strip()

			if health_found_flag :
				disk_health_flag = ( health_list_item.split()[-1] == "PASSED" )
				break

			if health_list_item == "=== START OF READ SMART DATA SECTION ===" :
				health_found_flag = True
		return disk_health_flag


class DisksSmart(service.FunctionObject) :
	@service.functionSignal(SMART_METHODS_NAMESPACE)
	def devicesChanged(self) :
		pass


##### Public classes #####
class Service(service.Service) :
	def __init__(self) :
		service.Service.__init__(self)

		#####

		self.__udev_client = gudev.Client(["block"])

		self.__disks_smart = DisksSmart(DISKS_SMART_OBJECT_NAME, self)


	### Public ###

	def initService(self) :
		shared.Functions.addShared(DISKS_SMART_SHARED_NAME)
		shared.Functions.addSharedObject(DISKS_SMART_SHARED_NAME, self.__disks_smart)

		logger.verbose("{mod}: First devices request...")
		disks_smart_shared = shared.Functions.shared(DISKS_SMART_SHARED_NAME)
		disks_filter_regexp = re.compile(config.value(SERVICE_NAME, "disks_filter"))
		devices_count = 0
		for device in self.__udev_client.query_by_subsystem("block") :
			device_name = device.get_name()
			if disks_filter_regexp.match(device_name) :
				disks_smart_shared.addSharedObject(device_name, Disk(device.get_device_file(),
					dbus_tools.joinPath(DISKS_SMART_SHARED_NAME, device_name), self))
				devices_count += 1
		logger.verbose("{mod}: Added %d devices" % (devices_count))

		self.__udev_client.connect("uevent", self.udevEvent)
		logger.verbose("{mod}: Start polling udev events for \"block\"")

	def closeService(self) :
		self.__udev_client.disconnect_by_func(self.udevEvent)
		logger.verbose("{mod}: Stop polling udev events for \"block\"")

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "disks_filter", "^[(sd)(hd)][a-z]+$", str),
			(SERVICE_NAME, "smartctl_prog_path", "/usr/sbin/smartctl", str)
		]


	### Private ###

	def udevEvent(self, udev_client, action, device) :
		disks_smart_shared = shared.Functions.shared(DISKS_SMART_SHARED_NAME)
		registered_devices_list = disks_smart_shared.sharedObjects().keys() 

		if re.match(config.value(SERVICE_NAME, "disks_filter"), device.get_name()) :
			device_name = device.get_name()
			device_path = device.get_device_file()

			if action == "add" and not device in registered_devices_list :
				disks_smart_shared.addSharedObject(device_name, Disk(device_path,
					dbus_tools.joinPath(DISKS_SMART_SHARED_NAME, device_name), self))
				self.__disks_smart.devicesChanged()
				logger.debug("{mod}: Added SMART disk \"%s\"" % (device_path))

			elif device.get_action() == "remove" and device_name in registered_devices_list :
				disks_smart_shared.sharedObject(device_name).removeFromConnection()
				disks_smart_shared.removeSharedObject(device_name)
				self.__disks_smart.devicesChanged()
				logger.debug("{mod}: Removed SMART disk \"%s\"" % (device_path))

