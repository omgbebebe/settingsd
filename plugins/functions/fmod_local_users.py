# -*- coding: utf-8 -*-


import os
import re
import pwd
import spwd
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
SERVICE_NAME = "local_users"

LOCAL_USERS_SHARED_NAME = "local_users"

LOCAL_USERS_OBJECT_NAME = "local_users"

LOCAL_USER_METHODS_NAMESPACE = "localUser"
LOCAL_USERS_METHODS_NAMESPACE = "localUsers"


##### Private classes #####
class LocalUser(service.FunctionObject) :
	def __init__(self, user_name, object_path, service_object = None) :
		service.FunctionObject.__init__(self, object_path, service_object)

		self.__user_name = user_name


	### DBus methods ###

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="s")
	def realName(self) :
		return self.__user_name

	###

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, in_signature="i", out_signature="i")
	def setUid(self, uid) :
		if uid < 0 :
			raise validators.ValidatorError("Incorrect UID %d" % (uid))

		logger.verbose("{mod}: Request to change uid for local user \"%s\", new uid=%d" % (self.__user_name, uid))

		return tools.process.execProcess("%s -u %d %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			uid, self.__user_name ), False)[2]

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="i")
	def uid(self) :
		return pwd.getpwnam(self.__user_name).pw_uid

	###

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, in_signature="i", out_signature="i")
	def setGid(self, gid) :
		if gid < 0 :
			raise validators.ValidatorError("Incorrect GID %d" % (gid))

		logger.verbose("{mod}: Request to change gid for local user \"%s\", new gid=%d" % (self.__user_name, gid))

		return tools.process.execProcess("%s -g %d %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			gid, self.__user_name ), False)[2]

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="i")
	def gid(self) :
		return pwd.getpwnam(self.__user_name).pw_gid

	###

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def setHomePath(self, path) :
		if re.match(r"^[./\w\d]*$", path) == None :
			raise validators.ValidatorError("Incorrect symbols in string \"%s\"" % (path))

		logger.verbose("{mod}: Request to change home for local user \"%s\", new home=\"%s\"" % (self.__user_name, path))

		return tools.process.execProcess("%s -d \'%s\' %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			path, self.__user_name ), False)[2]

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="s")
	def homePath(self) :
		return pwd.getpwnam(self.__user_name).pw_dir

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def setShell(self, path) :
		if re.match(r"^[./\w\d]*$", path) == None :
			raise validators.ValidatorError("Incorrect symbols in string \"%s\"" % (path))

		logger.verbose("{mod}: Request to change shell for local user \"%s\", new shell=\"%s\"" % (self.__user_name, path))

		return tools.process.execProcess("%s -s \'%s\' %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			path, self.__user_name ), False)[2]

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="s")
	def shell(self) :
		return pwd.getpwnam(self.__user_name).pw_shell

	###

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, in_signature="s", out_signature="i")
	def setComment(self, text) :
		if re.match(r"^[@<>./\w\d \t]*$", text) == None :
			raise validators.ValidatorError("Incorrect symbols in string \"%s\"" % (text))

		logger.verbose("{mod}: Request to change comment for local user \"%s\", new comment=\"%s\"" % (self.__user_name, text))

		return tools.process.execProcess("%s -c \'%s\' %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			text, self.__user_name ), False)[2]

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="s")
	def comment(self) :
		return pwd.getpwnam(self.__user_name).pw_gecos

	###

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, in_signature="b", out_signature="i")
	def setLock(self, lock_flag) :
		(lock_arg, lock_str) = ( ("-L", "lock") if lock_flag else ("-U", "unlock") )

		logger.verbose("{mod}: Request to %s local user \"%s\"" % (lock_str))

		return tools.process.execProcess("%s %s %s" % ( config.value(SERVICE_NAME, "usermod_bin"),
			lock_arg, self.__user_name ), False)[2]

	@service.functionMethod(LOCAL_USER_METHODS_NAMESPACE, out_signature="b")
	def isLocked(self) :
		passwd = pwd.getpwnam(self.__user_name).pw_passwd
		if len(passwd) > 0 :
			passwd = ( passwd if passwd != "x" else spwd.getspnam(self.__user_name).sp_pwd )
			return ( len(passwd) > 0 and passwd[0] == "!" )
		return False


class LocalUsers(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(LOCAL_USERS_METHODS_NAMESPACE, in_signature="sii", out_signature="i")
	def addUser(self, user_name, uid, gid) :
		user_name = validators.os.validUserName(user_name)
		(uid_arg, uid_str) = ( ("-u %d" % (uid), str(uid)) if uid >= 0 else ("", "auto") )
		(gid_arg, gid_str) = ( ("-g %d" % (gid), str(gid)) if gid >= 0 else ("", "auto") )

		logger.verbose("{mod}: Request to add local user \"%s\" with uid=%s and gid=%s" % (user_name, uid_str, gid_str))

		return tools.process.execProcess("%s %s %s %s" % (config.value(SERVICE_NAME, "useradd_bin"),
			uid_arg, gid_arg, user_name))

	@service.functionMethod(LOCAL_USERS_METHODS_NAMESPACE, in_signature="sb", out_signature="i")
	def removeUser(self, user_name, remove_data_flag) :
		user_name = validators.os.validUserName(user_name)
		(remove_data_arg, remove_data_str) = ( ("-r", " and its data") if remove_data_flag else ("", "") )

		logger.verbose("{mod}: Request to remove local user \"%s\"%s" % (user_name, remove_data_str))
		return tools.process.execProcess("%s %s %s" % (config.value(SERVICE_NAME, "userdel_bin"),
			remove_data_arg, user_name), False)[2]

	###

	@service.functionMethod(LOCAL_USERS_METHODS_NAMESPACE, out_signature="i")
	def minUid(self) :
		return self.loginDefsValue("UID_MIN")

	@service.functionMethod(LOCAL_USERS_METHODS_NAMESPACE, out_signature="i")
	def maxUid(self) :
		return self.loginDefsValue("UID_MAX")

	@service.functionMethod(LOCAL_USERS_METHODS_NAMESPACE, out_signature="i")
	def minSystemUid(self) :
		return self.loginDefsValue("SYS_UID_MIN")

	@service.functionMethod(LOCAL_USERS_METHODS_NAMESPACE, out_signature="i")
	def maxSystemUid(self) :
		return self.loginDefsValue("SYS_UID_MAX")


	### DBus signals ###

	@service.functionSignal(LOCAL_USERS_METHODS_NAMESPACE)
	def usersChanged(self) :
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

		self.__local_users = LocalUsers(LOCAL_USERS_OBJECT_NAME, self)


	### Public ###

	def initService(self) :
		shared.Functions.addShared(LOCAL_USERS_SHARED_NAME)
		shared.Functions.addSharedObject(LOCAL_USERS_OBJECT_NAME, self.__local_users)

		logger.verbose("{mod}: First local users request...")
		local_users_shared = shared.Functions.shared(LOCAL_USERS_SHARED_NAME)
		user_count = 0
		for user_name in self.localUsers() :
			dbus_user_name = re.sub(r"[^\w\d_]", "_", user_name)
			local_users_shared.addSharedObject(dbus_user_name, LocalUser(user_name,
				tools.dbus.joinPath(SERVICE_NAME, dbus_user_name), self))
			user_count += 1
		logger.verbose("{mod}: Added %d local users" % (user_count))

		passwd_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "passwd_conf"))
		self.__watch_manager.add_watch(passwd_config_subdir_path, pyinotify.IN_DELETE|pyinotify.IN_CREATE|pyinotify.IN_MOVED_TO, rec=True)
		self.start()
		logger.verbose("{mod}: Start polling inotify events for \"%s\"" % (passwd_config_subdir_path))

	def closeService(self) :
		passwd_config_subdir_path = os.path.dirname(config.value(SERVICE_NAME, "passwd_conf"))
		self.__watch_manager.rm_watch(self.__watch_manager.get_wd(passwd_config_subdir_path))
		self.stop()
		logger.verbose("{mod}: Stop polling inotify events for \"%s\"" % (passwd_config_subdir_path))

	###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "useradd_bin", "/usr/sbin/useradd", str),
			(SERVICE_NAME, "userdel_bin", "/usr/sbin/userdel", str),
			(SERVICE_NAME, "usermod_bin", "/usr/sbin/usermod", str),
			(SERVICE_NAME, "passwd_conf", "/etc/passwd", str),
			(SERVICE_NAME, "shadow_conf", "/etc/shadow", str),
			(SERVICE_NAME, "login_defs_conf", "/etc/login.defs", str)
		]


	### Private ###

	def inotifyEvent(self, event) :
		if event.dir or not event.pathname in ( config.value(SERVICE_NAME, "passwd_conf"),
			config.value(SERVICE_NAME, "shadow_conf"), config.value(SERVICE_NAME, "login_defs_conf") ) :

			return

		user_names_list = self.localUsers()
		dbus_user_names_list = [ re.sub(r"[^\w\d_]", "_", item) for item in user_names_list ]

		local_users_shared = shared.Functions.shared(LOCAL_USERS_SHARED_NAME)

		for count in xrange(len(user_names_list)) :
			if not local_users_shared.hasSharedObject(dbus_user_names_list[count]) :
				local_users_shared.addSharedObject(dbus_user_names_list[count], LocalUser(user_names_list[count],
					tools.dbus.joinPath(SERVICE_NAME, dbus_user_names_list[count]), self))
				logger.verbose("{mod}: Added local user \"%s\"" % (user_names_list[count]))

		for dbus_user_name in local_users_shared.sharedObjects().keys() :
			if not dbus_user_name in dbus_user_names_list :
				user_name = local_users_shared.sharedObject(dbus_user_name).realName()
				local_users_shared.sharedObject(dbus_user_name).removeFromConnection()
				local_users_shared.removeSharedObject(dbus_user_name)
				logger.verbose("{mod}: Removed local user \"%s\"" % (user_name))

		self.__local_users.usersChanged()

	###

	def localUsers(self) :
		user_name_regexp = re.compile(r"(^[a-z_][a-z0-9_-]*):")

		try :
			passwd_config_file = open(config.value(SERVICE_NAME, "passwd_conf"))
		except :
			logger.attachException()
			return []

		user_names_list = []
		for passwd_record in passwd_config_file.read().split("\n") :
			user_name_regexp_match = user_name_regexp.match(passwd_record)
			if user_name_regexp_match != None :
				user_names_list.append(user_name_regexp_match.group(1))

		try :
			passwd_config_file.close()
		except : pass

		return user_names_list

