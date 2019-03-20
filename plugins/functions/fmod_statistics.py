# -*- coding: utf-8 -*-


import re

from settingsd import service
from settingsd import shared

import settingsd.tools as tools
import settingsd.tools.dbus
import psutil
from os import getloadavg


##### Private constants #####
SERVICE_NAME = "statistics"

STATISTICS_SHARED_NAME = "statistics"
CPU_SHARED_NAME = "cpu"

STATISTICS_OBJECT_NAME = "statistics"
MEMORY_OBJECT_NAME = "memory"
CPU_OBJECT_NAME = "cpu"

STATISTICS_METHODS_NAMESPACE = "statistics"
MEMORY_METHODS_NAMESPACE = "statistics.memory"
CPU_METHODS_NAMESPACE = "statistics.cpu"


##### Private classes #####
class Statistics(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(STATISTICS_METHODS_NAMESPACE, out_signature="ad")
	def loadAverage(self) :
		loadavg_file = open("/proc/loadavg")
		levels_list = [ float(level) for level in loadavg_file.read().split(" ")[:3] ]
		try :
			loadavg_file.close()
		except : pass
		return levels_list

	@service.functionMethod(STATISTICS_METHODS_NAMESPACE, out_signature="d")
	def uptime(self) :
		uptime_file = open("/proc/uptime")
		uptime = float(uptime_file.read().split()[0])
		try :
			uptime_file.close()
		except : pass
		return uptime


class Memory(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(MEMORY_METHODS_NAMESPACE, out_signature="t")
	def memoryFull(self) :
		return psutil.virtual_memory().total

	@service.functionMethod(MEMORY_METHODS_NAMESPACE, out_signature="t")
	def memoryFree(self) :
		return psutil.virtual_memory().available

	@service.functionMethod(MEMORY_METHODS_NAMESPACE, out_signature="t")
	def swapFull(self) :
		return psutil.swap_memory().total

	@service.functionMethod(MEMORY_METHODS_NAMESPACE, out_signature="t")
	def swapFree(self) :
		swap = psutil.swap_memory()
		return swap.total - swap.used


	### Private ###

	def meminfoSum(self, *args_list) :
		meminfo_file = open("/proc/meminfo")
		meminfo_records_list = meminfo_file.read().split("\n")
		try :
			meminfo_file.close()
		except : pass

		sum = 0
		for meminfo_records_list_item in meminfo_records_list :
			value_list = re.split(r"[\s:]+", meminfo_records_list_item)
			if len(value_list) != 3 :
				continue

			if value_list[0] in args_list : 
				sum += int(value_list[1])

		return sum


class Cpu(service.FunctionObject) :
	def __init__(self, cpu_name, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__cpu_name = cpu_name

		#####

		self.__previous_used = -1
		self.__previous_full = -1

		self.__cpuinfo_cache_dict = {}

		#####

		self.loadPercent()


	### DBus methods ###

	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="s")
	def modelName(self) :
		return self.cpuinfoSection("model name", True)

	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="i")
	def physicalId(self) :
		id = self.cpuinfoSection("physical id", True)
		if len(id) != 0 :
			return int(id)
		else :
			return -1

	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="d")
	def frequencyMhz(self) :
		frequency = self.cpuinfoSection("cpu MHz")
		if len(frequency) != 0 :
			return float(frequency)
		else :
			return -1

	###
	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="i")
	def cpuCount(self):
		return psutil.cpu_count()

	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="a{sd}")
	def cpuTimes(self):
		times = psutil.cpu_times_percent()
		return {
			'iowait': times.iowait,
			'softirq': times.softirq,
			'sys': times.system,
			'user': times.user
		}

	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="ad")
	def loadAverage(self):
		return getloadavg()

	@service.functionMethod(CPU_METHODS_NAMESPACE, out_signature="d")
	def loadPercent(self) :
		stat_file = open("/proc/stat")
		stat_file_records_list = stat_file.read().split("\n")
		try :
			stat_file.close()
		except : pass

		for stat_file_records_list_item in stat_file_records_list :
			if stat_file_records_list_item.startswith(self.cpuName()) :
				(cpu, nice, system, idle) = [ float(cpu_stat_item) for cpu_stat_item in re.split(r"\s+", stat_file_records_list_item)[1:5] ]
				used = cpu + system + nice
				full = cpu + nice + system + idle

				if self.__previous_full == -1 :
					load_percent = 0
				else :
					load_percent = (100 * (used - self.__previous_used)) / (full - self.__previous_full)

				self.__previous_used = used
				self.__previous_full = full

				return load_percent
		return -1


	### Private ###

	def cpuName(self) :
		return self.__cpu_name

	###

	def cpuinfoSection(self, section_name, use_cache_flag = False) :
		if self.__cpuinfo_cache_dict.has_key(section_name) and use_cache_flag :
			return self.__cpuinfo_cache_dict[section_name]

		cpu_id = self.cpuName().split("cpu")[1]

		cpuinfo_file = open("/proc/cpuinfo")
		cpuinfo_processors_list = cpuinfo_file.read().split("\n\n")
		try :
			cpuinfo_file.close()
		except : pass

		for cpuinfo_processors_list_item in cpuinfo_processors_list :
			if len(cpuinfo_processors_list_item) == 0 :
				continue

			for cpu_record in cpuinfo_processors_list_item.split("\n") :
				if len(cpu_record) == 0 :
					continue

				(name, value) = cpu_record.split(":")
				name = name.strip()
				value = value.strip()

				if name == "processor" and value != cpu_id :
					break
				elif name == section_name :
					self.__cpuinfo_cache_dict[name] = value
					return value

		return ""


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addShared(STATISTICS_SHARED_NAME)

		###

		shared.Functions.addSharedObject(STATISTICS_OBJECT_NAME, Statistics(STATISTICS_OBJECT_NAME, self))

		###

		shared.Functions.shared(STATISTICS_SHARED_NAME).addSharedObject(MEMORY_OBJECT_NAME,
			Memory(tools.dbus.joinPath(STATISTICS_SHARED_NAME, MEMORY_OBJECT_NAME), self))

		###

		shared.Functions.shared(STATISTICS_SHARED_NAME).addShared(CPU_SHARED_NAME)
		stat_file = open("/proc/stat")
		cpu_names_list = [ re.split(r"\s+", stat_record)[0] for stat_record in stat_file.read().split("\n")
			if re.match(r"cpu\d+", stat_record) != None ]
		try :
			stat_file.close()
		except : pass

		shared.Functions.shared(STATISTICS_SHARED_NAME).addSharedObject(CPU_OBJECT_NAME,
			Cpu(CPU_OBJECT_NAME, tools.dbus.joinPath(STATISTICS_SHARED_NAME, CPU_OBJECT_NAME), self))
		for cpu_names_list_item in cpu_names_list :
			shared.Functions.shared(STATISTICS_SHARED_NAME).shared(CPU_SHARED_NAME).addSharedObject(cpu_names_list_item,
				Cpu(cpu_names_list_item, tools.dbus.joinPath(STATISTICS_SHARED_NAME, CPU_SHARED_NAME, cpu_names_list_item), self))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

