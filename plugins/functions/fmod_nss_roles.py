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
SERVICE_NAME = "nss_roles"

NSS_ROLES_SHARED_NAME = "nss_roles"

NSS_ROLES_OBJECT_NAME = "nss_roles"

NSS_ROLE_METHODS_NAMESPACE = "nssRole"
NSS_ROLES_METHODS_NAMESPACE = "nssRoles"


##### Private classes #####
class NssRole(service.FunctionObject) :
	def __init__(self, role_name, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__role_name = role_name


	### DBus methods ###

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, out_signature="s")
	def realName(self) :
		return self.__role_name

	###

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, out_signature="i")
	def rid(self) :
		return grp.getgrnam(self.__role_name).gr_gid

	###

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def addGroup(self, group_name) :
		group_name = validators.os.validGroupName(group_name)

		gid = grp.getgrnam(group_name).gr_gid
		rid = grp.getgrnam(self.__role_name).gr_gid

		logger.verbose("{mod}: Request to add group \"%s\" to NSS role \"%s\"" % (group_name, self.__role_name))

		editor = tools.editors.PlainEditor(delimiter=":", spaces_list=[], quotes_list=[])
		editor.open(config.value(SERVICE_NAME, "role_conf"))

		role_gids_list = editor.value(str(rid))
		if len(role_gids_list) > 0 and len(role_gids_list[-1]) > 0 :
			if not str(gid) in role_gids_list[-1].split(",") :
				editor.setValue(str(rid), ",".join((role_gids_list[-1], str(gid))))
				editor.save()
				editor.close()
				return 0
			else :
				logger.verbose("{mod}: Group \"%s\" is already in role \"%s\"" % (group_name, self.__role_name))
				editor.close()
				return 1

		editor.setValue(str(rid), str(gid))
		editor.save()
		editor.close()
		return 0

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeGroup(self, group_name) :
		group_name = validators.os.validGroupName(group_name)
		gid = grp.getgrnam(group_name).gr_gid
		rid = grp.getgrnam(self.__role_name).gr_gid

		logger.verbose("{mod}: Request to remove group \"%s\" from NSS role \"%s\"" % (group_name, self.__role_name))

		editor = tools.editors.PlainEditor(delimiter=":", spaces_list=[], quotes_list=[])
		editor.open(config.value(SERVICE_NAME, "role_conf"))

		role_gids_list = editor.value(str(rid))
		if len(role_gids_list) > 0 and len(role_gids_list[-1]) > 0 :
			gids_list = role_gids_list[-1].split(",")
			if str(gid) in gids_list :
				gids_list.remove(str(gid))
				editor.setValue(str(rid), ",".join(gids_list))
				editor.save()
				editor.close()
				return 0
			else :
				logger.verbose("{mod}: Group \"%s\" is not included in role \"%s\"" % (group_name, self.__role_name))
				editor.close()
				return 1

		editor.close()
		return 1

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, out_signature="as")
	def groups(self) :
		editor = tools.editors.PlainEditor(delimiter=":", spaces_list=[], quotes_list=[])
		editor.open(config.value(SERVICE_NAME, "role_conf"))
		role_gids_list = editor.value(str(grp.getgrnam(self.__role_name).gr_gid))
		editor.close()
		if len(role_gids_list) > 0 :
			return [ grp.getgrgid(item).gr_name for item in role_gids_list[-1].split(",") ]
		else :
			return []

	###

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def addUser(self, user_name) :
		user_name = validators.os.validUserName(user_name)

		logger.verbose("{mod}: Request to add user \"%s\" to NSS role \"%s\"" % (user_name, self.__role_name))
		return tools.process.execProcess("%s -a -G %s %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			self.__role_name, user_name ), False)[2]

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeUser(self, user_name) :
		user_name = validators.os.validUserName(user_name)

		users_list = grp.getgrnam(self.__role_name).gr_mem
		users_list.remove(self.__role_name)

		logger.verbose("{mod}: Request to remove user \"%s\" from NSS role \"%s\"" % (user_name, self.__role_name))
		return tools.process.execProcess("%s -G %s %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			",".join(users_list), user_name ), False)[2]

	@service.functionMethod(NSS_ROLE_METHODS_NAMESPACE, out_signature="as")
	def users(self) :
		return grp.getgrnam(self.__role_name).gr_mem


class NssRoles(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(NSS_ROLES_METHODS_NAMESPACE, in_signature="sas", out_signature="i")
	def addRole(self, role_name, group_names_list) :
		role_name = validators.os.validGroupName(role_name)
		group_names_list = [ validators.os.validGroupName(item) for item in group_names_list ]

		rid = grp.getgrnam(role_name).gr_gid

		if len(gids) == 0 :
			logger.verbose("{mod}: Ignored an attempt to create an empty NSS role \"%s\" (rid=%d)" % (role_name, rid))
			return 1

		logger.verbose("{mod}: Request to add NSS role \"%s\" (rid=%d) with groups \"%s\"" % (role_name, rid, str(group_names_list)))

		editor = tools.editors.PlainEditor(delimiter=":", spaces_list=[], quotes_list=[])
		editor.open(config.value(SERVICE_NAME, "role_conf"))
		editor.setValue(str(rid), ",".join([ grp.getgrnam(item).gr_gid for item in group_names_list ]))
		editor.save()
		editor.close()

		return 0

	@service.functionMethod(NSS_ROLES_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def removeRole(self, role_name) :
		role_name = validators.os.validGroupName(role_name)

		rid = grp.getgrnam(role_name).gr_gid

		logger.verbose("{mod}: Request to remove NSS role \"%s\" (rid=%d)" % (role_name, rid))

		editor = tools.editors.PlainEditor(delimiter=":", spaces_list=[], quotes_list=[])
		editor.open(config.value(SERVICE_NAME, "role_conf"))
		editor.setValue(str(rid), None)
		editor.save()
		editor.close()

		return 0


	### DBus signals ###

	@service.functionSignal(NSS_ROLES_METHODS_NAMESPACE)
	def rolesChanged(self) :
		pass


##### Public classes #####
class Service(service.Service, pyinotify.ThreadedNotifier) :
	def __init__(self) :
		service.Service.__init__(self)

		self.__watch_manager = pyinotify.WatchManager()
		pyinotify.ThreadedNotifier.__init__(self, self.__watch_manager, type("EventsHandler", (pyinotify.ProcessEvent,),
			{ "process_default" : self.inotifyEvent })())

		#####

		self.__nss_roles = NssRoles(NSS_ROLES_OBJECT_NAME, self)


	### Public ###

	def initService(self) :
		shared.Functions.addShared(NSS_ROLES_SHARED_NAME)
		shared.Functions.addSharedObject(NSS_ROLES_OBJECT_NAME, self.__nss_roles)

		logger.verbose("{mod}: First NSS roles request...")
		nss_roles_shared = shared.Functions.shared(NSS_ROLES_SHARED_NAME)
		role_count = 0
		for role_name in self.nssRoles() :
			dbus_role_name = role_name.replace("-", "_")
			nss_roles_shared.addSharedObject(dbus_role_name, NssRole(role_name,
				tools.dbus.joinPath(SERVICE_NAME, dbus_role_name), self))
			role_count += 1
		logger.verbose("{mod}: Added %d NSS roles" % (role_count))

		role_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "role_conf"))
		self.__watch_manager.add_watch(role_config_subdir_path, pyinotify.IN_DELETE|pyinotify.IN_CREATE|pyinotify.IN_MOVED_TO, rec=True)
		self.start()
		logger.verbose("{mod}: Start polling inotify events for \"%s\"" % (role_config_subdir_path))

	def closeService(self) :
		role_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "role_conf"))
		self.__watch_manager.rm_watch(self.__watch_manager.get_wd(role_config_subdir_path))
		self.stop()
		logger.verbose("{mod}: Stop polling inotify events for \"%s\"" % (role_config_subdir_path))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "usermod_bin", "/usr/sbin/usermod", str),
			(SERVICE_NAME, "group_conf", "/etc/group", str),
			(SERVICE_NAME, "role_conf", "/etc/role", str)
		]


	### Private ###

	def inotifyEvent(self, event) :
		if event.dir or not event.pathname in ( config.value(SERVICE_NAME, "role_conf"),
			config.value(SERVICE_NAME, "group_conf") ) :

			return

		role_names_list = self.nssRoles()
		dbus_role_names_list = [ item.replace("-", "_") for item in role_names_list ]

		nss_roles_shared = shared.Functions.shared(NSS_ROLES_SHARED_NAME)

		for count in xrange(len(roles_names_list)) :
			if not nss_roles_shared.hasSharedObject(dbus_role_names_list[count]) :
				nss_roles_shared.addSharedObject(dbus_role_names_list[count], NssRole(role_names_list[count],
					tools.dbus.joinPath(SERVICE_NAME, dbus_role_names_list[count]), self))
				logger.verbose("{mod}: Added NSS role \"%s\"" % (role_names_list[count]))

		for dbus_role_name in nss_roles_shared.sharedObjects().keys() :
			if not dbus_role_name in dbus_role_names_list :
				role_name = nss_roles_shared.sharedObject(dbus_role_name).realName()
				nss_roles_shared.sharedObject(dbus_role_name).removeFromConnection()
				nss_roles_shared.removeSharedObject(dbus_role_name)
				logger.verbose("{mod}: Removed NSS role \"%s\"" % (role_name))

		self.__nss_roles.rolesChanged()

	###

	def nssRoles(self) :
		rid_regexp = re.compile(r"(^\d+):")

		try :
			role_config_file = open(config.value(SERVICE_NAME, "role_conf"))
		except :
			logger.attachException()
			return []

		role_names_list = []
		for role_record in role_config_file.read().split("\n") :
			rid_regexp_match = rid_regexp.match(role_record)
			if rid_regexp_match != None :
				try :
					role_names_list.append(grp.getgrgid(int(rid_regexp_match.group(1))).gr_name)
				except :
					logger.error("{mod}: Cannot resolve group name by gid")
					logger.attachException()

		try :
			role_config_file.close()
		except : pass

		return role_names_list

