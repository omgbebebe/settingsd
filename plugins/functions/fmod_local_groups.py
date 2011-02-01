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

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def addUser(self, user_name) :
		user_name = validators.os.validUserName(user_name)

		logger.verbose("{mod}: Request to add user \"%s\" to UNIX group \"%s\"" % (user_name, self.__group_name))
		return tools.process.execProcess("%s -a -G %s %s" % ( config.value(SERVICE_NAME, "usermod_prog_path"),
			self.__group_name, user_name ), False)[2]

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeUser(self, user_name) :
		user_name = validators.os.validUserName(user_name)

		users_list = grp.getgrnam(self.__group_name).gr_mem
		users_list.remove(self.__group_name)

		logger.verbose("{mod}: Request to remove user \"%s\" from UNIX group \"%s\"" % (user_name, self.__group_name))
		return tools.process.execProcess("%s -G %s %s" % ( config.value(SERVICE_NAME, "usermod_prog_path"),
			",".join(users_list), user_name ), False)[2]

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, out_signature="as")
	def users(self) :
		return grp.getgrnam(self.__group_name).gr_mem

	###

	@service.functionMethod(LOCAL_GROUP_METHODS_NAMESPACE, out_signature="i")
	def gid(self) :
		return grp.getgrnam(self.__group_name).gr_gid


class LocalGroups(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, in_signature="si", out_signature="i")
	def addGroup(self, group_name, gid) :
		group_name = validators.os.validGroupName(group_name)
		(gid_arg, gid_str) = ( ("-g %d" % (gid), str(gid)) if gid >= 0 else ("", "auto") )

		logger.verbose("{mod}: Request to add UNIX group \"%s\" with gid=%s" % (group_name, gid_str))

		return tools.process.execProcess("%s %s %s" % (config.value(SERVICE_NAME, "groupadd_prog_path"), gid_arg, group_name))

	@service.functionMethod(LOCAL_GROUPS_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeGroup(self, group_name) :
		group_name = validators.os.validGroupName(group_name)

		logger.verbose("{mod}: Request to remove UNIX group \"%s\"" % (group_name))
		return tools.process.execProcess("%s %s" % (config.value(SERVICE_NAME, "groupdel_prog_path"), group_name), False)[2]


	### DBus signals ###

	@service.functionSignal(LOCAL_GROUPS_METHODS_NAMESPACE)
	def groupsChanged(self) :
		pass


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

		logger.verbose("{mod}: First UNIX groups request...")
		local_groups_shared = shared.Functions.shared(LOCAL_GROUPS_SHARED_NAME)
		group_count = 0
		for group_name in self.localGroups() :
			dbus_group_name = group_name.replace("-", "_")
			local_groups_shared.addSharedObject(dbus_group_name, LocalGroup(group_name,
				tools.dbus.joinPath(SERVICE_NAME, dbus_group_name), self))
			group_count += 1
		logger.verbose("{mod}: Added %d UNIX groups" % (group_count))

		group_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "group_config_file_path"))
		self.__watch_manager.add_watch(group_config_subdir_path, pyinotify.IN_DELETE|pyinotify.IN_CREATE|pyinotify.IN_MOVED_TO, rec=True)
		self.start()
		logger.verbose("{mod}: Start polling inotify events for \"%s\"" % (group_config_subdir_path))

	def closeService(self) :
		group_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "group_config_file_path"))
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
			(SERVICE_NAME, "groupadd_prog_path", "/usr/sbin/groupadd", str),
			(SERVICE_NAME, "groupdel_prog_path", "/usr/sbin/groupdel", str),
			(SERVICE_NAME, "usermod_prog_path", "/usr/sbin/usermod", str),
			(SERVICE_NAME, "group_config_file_path", "/etc/group", str)
		]


	### Private ###

	def inotifyEvent(self, event) :
		if event.dir or event.pathname != config.value(SERVICE_NAME, "group_config_file_path") :
			return

		group_names_list = self.localGroups()
		dbus_group_names_list = [ item.replace("-", "_") for item in group_names_list ]

		local_groups_shared = shared.Functions.shared(LOCAL_GROUPS_SHARED_NAME)

		for count in xrange(len(group_names_list)) :
			if not local_groups_shared.hasSharedObject(dbus_group_names_list[count]) :
				local_groups_shared.addSharedObject(dbus_group_names_list[count], LocalGroup(group_names_list[count],
					tools.dbus.joinPath(SERVICE_NAME, dbus_group_names_list[count]), self))
				logger.verbose("{mod}: Added UNIX group \"%s\"" % (group_names_list[count]))

		for dbus_group_name in local_groups_shared.sharedObjects().keys() :
			if not dbus_group_name in dbus_group_names_list :
				group_name = local_groups_shared.sharedObject(dbus_group_name).realName()
				local_groups_shared.sharedObject(dbus_group_name).removeFromConnection()
				local_groups_shared.removeSharedObject(dbus_group_name)
				logger.verbose("{mod}: Removed UNIX group \"%s\"" % (group_name))

		self.__local_groups.groupsChanged()

	###

	def localGroups(self) :
		group_name_regexp = re.compile(r"(^[a-z_][a-z0-9_-]*):")

		group_config_file = open(config.value(SERVICE_NAME, "group_config_file_path"))

		group_names_list = []
		for group_record in group_config_file.read().split("\n") :
			group_name_regexp_match = group_name_regexp.match(group_record)
			if group_name_regexp_match != None :
				group_names_list.append(group_name_regexp_match.group(1))

		try :
			group_config_file.close()
		except : pass

		return group_names_list

