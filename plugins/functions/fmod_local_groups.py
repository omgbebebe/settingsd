# -*- coding: utf-8 -*-


import os
import re
import grp
import pyinotify

from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger

import settingsd.validators as validators
import settingsd.validators.os

import settingsd.tools as tools
import settingsd.tools.dbus
import settingsd.tools.process
import settingsd.tools.editors


##### Private constants #####
SERVICE_NAME = "local_groups"

LOCAL_GROUPS_SHARED_NAME = "local_groups"

LOCAL_GROUPS_OBJECT_NAME = "local_groups"

LOCAL_GROUP_METHODS_NAMESPACE = "localGroup"
LOCAL_GROUPS_METHODS_NAMESPACE = "localGroups"


##### Private classes #####
class LocalGroup(service.FunctionObject) :
	def __init__(self, group_name, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__group_name = group_name


	### DBus methods ###

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, out_signature="s")
	def realName(self) :
		return self.__group_name

	###

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, in_signature="i", out_signature="i")
	def setGid(self, gid) :
		if gid < 0 :
			raise validators.ValidatorError("Incorrect GID %d" % (gid))

		logger.verbose("{mod}: Request to change gid for local group \"%s\", new gid=%d" % (self.__group_name, gid))

		proc_args_list = [config.value(SERVICE_NAME, "groupmod_bin"), "-g", str(gid), self.__group_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, out_signature="i")
	def gid(self) :
		return grp.getgrnam(self.__group_name).gr_gid

	###

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def addUser(self, user_name) :
		user_name = validators.os.validUserName(user_name)

		logger.verbose("{mod}: Request to add user \"%s\" to local group \"%s\"" % (user_name, self.__group_name))

		proc_args_list = [config.value(SERVICE_NAME, "usermod_bin"), "-a", "-G", self.__group_name, user_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeUser(self, user_name) :
		user_name = validators.os.validUserName(user_name)

		users_list = grp.getgrnam(self.__group_name).gr_mem
		users_list.remove(self.__group_name)
		users = ",".join(users_list)

		logger.verbose("{mod}: Request to remove user \"%s\" from local group \"%s\"" % (user_name, self.__group_name))

		proc_args_list = [config.value(SERVICE_NAME, "usermod_bin"), "-G", users, user_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, out_signature="as")
	def users(self) :
		return grp.getgrnam(self.__group_name).gr_mem


class LocalGroups(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, in_signature="si", out_signature="i")
	def addGroup(self, group_name, gid) :
		group_name = validators.os.validGroupName(group_name)
		(gid_args_list, gid_str) = ( (["-g", str(gid)], str(gid)) if gid >= 0 else ([], "auto") )

		logger.verbose("{mod}: Request to add local group \"%s\" with gid=%s" % (group_name, gid_str))

		proc_args_list = [config.value(SERVICE_NAME, "groupadd_bin")] + gid_args_list + [group_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeGroup(self, group_name) :
		group_name = validators.os.validGroupName(group_name)

		logger.verbose("{mod}: Request to remove local group \"%s\"" % (group_name))

		proc_args_list = [config.value(SERVICE_NAME, "groupdel_bin"), group_name]
		return tools.process.execProcess(proc_args_list, fatal_flag = False)[2]

	###

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, out_signature="i")
	def minGid(self) :
		return self.loginDefsValue("GID_MIN")

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, out_signature="i")
	def maxGid(self) :
		return self.loginDefsValue("GID_MAX")

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, out_signature="i")
	def minSystemGid(self) :
		return self.loginDefsValue("SYS_GID_MIN")

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, out_signature="i")
	def maxSystemGid(self) :
		return self.loginDefsValue("SYS_GID_MAX")


	### DBus signals ###

	@service.functionSignal(LOCAL_GROUPS_METHODS_NAMESPACE)
	def groupsChanged(self) :
		pass


	### Private ###

	def loginDefsValue(self, variable_name) :
		editor = tools.editors.PlainEditor(delimiter = "", quotes_list = [])
		editor.open(config.value(SERVICE_NAME, "login_defs_conf"))
		values_list = editor.value(variable_name)
		editor.close()
		return ( int(values_list[-1]) if len(values_list) > 0 else -1 )


##### Public classes #####
class Service(service.Service, pyinotify.ThreadedNotifier) :
	def __init__(self) :
		service.Service.__init__(self)

		self.__watch_manager = pyinotify.WatchManager()
		pyinotify.ThreadedNotifier.__init__(self, self.__watch_manager, type("EventsHandler", (pyinotify.ProcessEvent,),
			{ "process_default" : self.inotifyEvent })())

		#####

		self.__local_groups = LocalGroups(LOCAL_GROUPS_OBJECT_NAME, self)


	### Public ###

	def initService(self) :
		shared.Functions.addShared(LOCAL_GROUPS_SHARED_NAME)
		shared.Functions.addSharedObject(LOCAL_GROUPS_OBJECT_NAME, self.__local_groups)

		logger.verbose("{mod}: First local groups request...")
		local_groups_shared = shared.Functions.shared(LOCAL_GROUPS_SHARED_NAME)
		group_count = 0
		for group_name in self.localGroups() :
			dbus_group_name = re.sub(r"[^\w\d_]", "_", group_name)
			local_groups_shared.addSharedObject(dbus_group_name, LocalGroup(group_name,
				tools.dbus.joinPath(SERVICE_NAME, dbus_group_name), self))
			group_count += 1
		logger.verbose("{mod}: Added %d local groups" % (group_count))

		group_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "group_conf"))
		self.__watch_manager.add_watch(group_config_subdir_path, pyinotify.IN_DELETE|pyinotify.IN_CREATE|pyinotify.IN_MOVED_TO, rec=True)
		self.start()
		logger.verbose("{mod}: Start polling inotify events for \"%s\"" % (group_config_subdir_path))

	def closeService(self) :
		group_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "group_conf"))
		self.__watch_manager.rm_watch(self.__watch_manager.get_wd(group_config_subdir_path))
		self.stop()
		logger.verbose("{mod}: Stop polling inotify events for \"%s\"" % (group_config_subdir_path))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "groupadd_bin", "/usr/sbin/groupadd", str),
			(SERVICE_NAME, "groupdel_bin", "/usr/sbin/groupdel", str),
			(SERVICE_NAME, "groupmod_bin", "/usr/sbin/groupmod", str),
			(SERVICE_NAME, "usermod_bin", "/usr/sbin/usermod", str),
			(SERVICE_NAME, "group_conf", "/etc/group", str),
			(SERVICE_NAME, "login_defs_conf", "/etc/login.defs", str)
		]


	### Private ###

	def inotifyEvent(self, event) :
		if event.dir or not event.pathname in ( config.value(SERVICE_NAME, "group_conf"),
			config.value(SERVICE_NAME, "login_defs_conf") ) :

			return

		group_names_list = self.localGroups()
		dbus_group_names_list = [ re.sub(r"[^\w\d_]", "_", item) for item in group_names_list ]

		local_groups_shared = shared.Functions.shared(LOCAL_GROUPS_SHARED_NAME)

		for count in xrange(len(group_names_list)) :
			if not local_groups_shared.hasSharedObject(dbus_group_names_list[count]) :
				local_groups_shared.addSharedObject(dbus_group_names_list[count], LocalGroup(group_names_list[count],
					tools.dbus.joinPath(SERVICE_NAME, dbus_group_names_list[count]), self))
				logger.verbose("{mod}: Added local group \"%s\"" % (group_names_list[count]))

		for dbus_group_name in local_groups_shared.sharedObjects().keys() :
			if not dbus_group_name in dbus_group_names_list :
				group_name = local_groups_shared.sharedObject(dbus_group_name).realName()
				local_groups_shared.sharedObject(dbus_group_name).removeFromConnection()
				local_groups_shared.removeSharedObject(dbus_group_name)
				logger.verbose("{mod}: Removed local group \"%s\"" % (group_name))

		self.__local_groups.groupsChanged()

	###

	def localGroups(self) :
		group_name_regexp = re.compile(r"(^[a-z_][a-z0-9_-]*):")

		try :
			group_config_file = open(config.value(SERVICE_NAME, "group_conf"))
		except :
			logger.attachException()
			return []

		group_names_list = []
		for group_record in group_config_file.read().split("\n") :
			group_name_regexp_match = group_name_regexp.match(group_record)
			if group_name_regexp_match != None :
				group_names_list.append(group_name_regexp_match.group(1))

		try :
			group_config_file.close()
		except : pass

		return group_names_list

